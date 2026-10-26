"""Impulse-based rigid-body simulation of a convex die thrown onto a table (z=0).

State: x (centroid), q (unit quaternion body->world), v, w (world angular velocity).
Contacts: every vertex below the table gets a Newton restitution + Coulomb friction impulse
(sequential impulses, a few passes per step). The die is deterministic: same start, same face.
"""
import numpy as np
from numba import njit, prange

G = 9.81


@njit(cache=True)
def qmul(a, b):
    return np.array([a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3],
                     a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2],
                     a[0]*b[2]-a[1]*b[3]+a[2]*b[0]+a[3]*b[1],
                     a[0]*b[3]+a[1]*b[2]-a[2]*b[1]+a[3]*b[0]])


@njit(cache=True)
def qrot(q):
    w, x, y, z = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-w*z), 2*(x*z+w*y)],
                     [2*(x*y+w*z), 1-2*(x*x+z*z), 2*(y*z-w*x)],
                     [2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x*x+y*y)]])


@njit(cache=True)
def cross(a, b):
    return np.array([a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]])


@njit(cache=True, fastmath=True)
def throw(Vb, Nb, Ibinv, x0, q0, v0, w0, e, mu, dt, tmax, rec_every, rec):
    """Vb: body vertices (centroid at 0), Nb: body face normals, Ibinv: inverse inertia (unit mass).
    Returns (face index on the table, t_rest, n_recorded). rec: (K, 7) array for trajectory (x,q).
    Allocation-free scalar inner loop."""
    x0_, x1, x2 = x0[0], x0[1], x0[2]
    qw, qx, qy, qz = q0[0], q0[1], q0[2], q0[3]
    v0_, v1, v2 = v0[0], v0[1], v0[2]
    w0_, w1, w2 = w0[0], w0[1], w0[2]
    nv = Vb.shape[0]
    R = np.empty((3, 3)); Ii = np.empty((3, 3)); T = np.empty((3, 3))
    r = np.empty(3)
    t = 0.0; calm = 0; nrec = 0; step = 0
    while t < tmax:
        # rotation matrix
        R[0,0]=1-2*(qy*qy+qz*qz); R[0,1]=2*(qx*qy-qw*qz); R[0,2]=2*(qx*qz+qw*qy)
        R[1,0]=2*(qx*qy+qw*qz); R[1,1]=1-2*(qx*qx+qz*qz); R[1,2]=2*(qy*qz-qw*qx)
        R[2,0]=2*(qx*qz-qw*qy); R[2,1]=2*(qy*qz+qw*qx); R[2,2]=1-2*(qx*qx+qy*qy)
        v2 -= G * dt
        if x2 < 1.8:
            for a_ in range(3):
                for b_ in range(3):
                    s_ = 0.0
                    for c_ in range(3):
                        s_ += Ibinv[a_, c_] * R[b_, c_]
                    T[a_, b_] = s_
            for a_ in range(3):
                for b_ in range(3):
                    s_ = 0.0
                    for c_ in range(3):
                        s_ += R[a_, c_] * T[c_, b_]
                    Ii[a_, b_] = s_
            for it in range(4):
                any_c = False
                for i in range(nv):
                    rz = R[2,0]*Vb[i,0]+R[2,1]*Vb[i,1]+R[2,2]*Vb[i,2]
                    if x2 + rz > 0.0:
                        continue
                    rx = R[0,0]*Vb[i,0]+R[0,1]*Vb[i,1]+R[0,2]*Vb[i,2]
                    ry = R[1,0]*Vb[i,0]+R[1,1]*Vb[i,1]+R[1,2]*Vb[i,2]
                    # vel = v + w x r
                    ux = v0_ + w1*rz - w2*ry
                    uy = v1 + w2*rx - w0_*rz
                    vn = v2 + w0_*ry - w1*rx
                    if vn >= 0.0:
                        continue
                    any_c = True
                    # rn = r x ez = (ry, -rx, 0); kn = 1 + ((Ii rn) x r)_z
                    ax = Ii[0,0]*ry - Ii[0,1]*rx
                    ay = Ii[1,0]*ry - Ii[1,1]*rx
                    kn = 1.0 + (ax*ry - ay*rx)
                    ee = e if vn < -0.3 else 0.0
                    jn = -(1.0 + ee) * vn / kn
                    Jx = 0.0; Jy = 0.0
                    sp = np.sqrt(ux*ux + uy*uy)
                    if sp > 1e-9:
                        tx = -ux/sp; ty = -uy/sp
                        # rt = r x t = (ry*0 - rz*ty, rz*tx - rx*0, rx*ty - ry*tx)
                        ptx = -rz*ty; pty = rz*tx; ptz = rx*ty - ry*tx
                        bx = Ii[0,0]*ptx + Ii[0,1]*pty + Ii[0,2]*ptz
                        by = Ii[1,0]*ptx + Ii[1,1]*pty + Ii[1,2]*ptz
                        bz = Ii[2,0]*ptx + Ii[2,1]*pty + Ii[2,2]*ptz
                        # (b x r) . t
                        cx = by*rz - bz*ry; cy = bz*rx - bx*rz
                        kt = 1.0 + cx*tx + cy*ty
                        jt = min(sp / kt, mu * jn)
                        Jx = jt*tx; Jy = jt*ty
                    v0_ += Jx; v1 += Jy; v2 += jn
                    # w += Ii (r x J)
                    cx = ry*jn - rz*Jy; cy = rz*Jx - rx*jn; cz = rx*Jy - ry*Jx
                    w0_ += Ii[0,0]*cx + Ii[0,1]*cy + Ii[0,2]*cz
                    w1 += Ii[1,0]*cx + Ii[1,1]*cy + Ii[1,2]*cz
                    w2 += Ii[2,0]*cx + Ii[2,1]*cy + Ii[2,2]*cz
                if not any_c:
                    break
        x0_ += v0_*dt; x1 += v1*dt; x2 += v2*dt
        h = 0.5*dt
        dw = h*(-w0_*qx - w1*qy - w2*qz)
        dx = h*( w0_*qw + w1*qz - w2*qy)
        dy = h*( w1*qw + w2*qx - w0_*qz)
        dz = h*( w2*qw + w0_*qy - w1*qx)
        qw += dw; qx += dx; qy += dy; qz += dz
        nq = 1.0/np.sqrt(qw*qw+qx*qx+qy*qy+qz*qz)
        qw *= nq; qx *= nq; qy *= nq; qz *= nq
        if x2 < 1.8:
            r20=2*(qx*qz-qw*qy); r21=2*(qy*qz+qw*qx); r22=1-2*(qx*qx+qy*qy)
            mz = 1e9
            for i in range(nv):
                z = x2 + r20*Vb[i,0]+r21*Vb[i,1]+r22*Vb[i,2]
                if z < mz:
                    mz = z
            if mz < 0.0:
                x2 -= mz
            spd = np.sqrt(v0_*v0_+v1*v1+v2*v2) + np.sqrt(w0_*w0_+w1*w1+w2*w2)
            if spd < 0.5:
                v0_ *= 0.995; v1 *= 0.995; v2 *= 0.995
                w0_ *= 0.995; w1 *= 0.995; w2 *= 0.995
            if spd < 0.06:
                calm += 1
            else:
                calm = 0
            if calm > 300:
                break
        if rec_every > 0 and step % rec_every == 0 and nrec < rec.shape[0]:
            rec[nrec,0]=x0_; rec[nrec,1]=x1; rec[nrec,2]=x2
            rec[nrec,3]=qw; rec[nrec,4]=qx; rec[nrec,5]=qy; rec[nrec,6]=qz
            nrec += 1
        t += dt
        step += 1
    q = np.array([qw, qx, qy, qz])
    Rf = qrot(q)
    best = -1; bz_ = 2.0
    for f in range(Nb.shape[0]):
        nz = Rf[2,0]*Nb[f,0]+Rf[2,1]*Nb[f,1]+Rf[2,2]*Nb[f,2]
        if nz < bz_:
            bz_ = nz; best = f
    if rec_every > 0 and nrec < rec.shape[0]:
        rec[nrec,0]=x0_; rec[nrec,1]=x1; rec[nrec,2]=x2
        rec[nrec,3]=qw; rec[nrec,4]=qx; rec[nrec,5]=qy; rec[nrec,6]=qz
        nrec += 1
    if t >= tmax:
        best = -1 - best
    return best, t, nrec


@njit(cache=True)
def rand_quat(u1, u2, u3):
    a = np.sqrt(1 - u1); b = np.sqrt(u1)
    return np.array([a*np.sin(2*np.pi*u2), a*np.cos(2*np.pi*u2), b*np.sin(2*np.pi*u3), b*np.cos(2*np.pi*u3)])


@njit(parallel=True, cache=True)
def monte_carlo(Vb, Nb, Ibinv, U, e, mu, dt, tmax, h0, vscale, wscale):
    """U: (M, 9) uniforms -> outcomes (M,)"""
    M = U.shape[0]
    out = np.zeros(M, np.int64)
    dummy = np.zeros((1, 7))
    for k in prange(M):
        u = U[k]
        q0 = rand_quat(u[0], u[1], u[2])
        x0 = np.array([0.0, 0.0, h0 * (0.5 + u[3])])
        v0 = np.array([vscale * (2*u[4]-1), vscale * (2*u[5]-1), 0.0])
        w0 = wscale * np.array([2*u[6]-1, 2*u[7]-1, 2*u[8]-1])
        f, t, n = throw(Vb, Nb, Ibinv, x0, q0, v0, w0, e, mu, dt, tmax, 0, dummy)
        out[k] = f
    return out


@njit(parallel=True, cache=True)
def basin(Vb, Nb, Ibinv, q0, x0, v0, wa, wb, e, mu, dt, tmax):
    """Grid over angular velocity: w = wa[i]*ex + wb[j]*ey. Returns face map."""
    A = wa.shape[0]; B = wb.shape[0]
    out = np.zeros((B, A), np.int64)
    dummy = np.zeros((1, 7))
    for idx in prange(A * B):
        j = idx // A; i = idx % A
        w0 = np.array([wa[i], wb[j], 0.0])
        f, t, n = throw(Vb, Nb, Ibinv, x0, q0, v0, w0, e, mu, dt, tmax, 0, dummy)
        out[j, i] = f
    return out


def prepare(V, F):
    from geom import mass_props, face_normals
    vol, c, I = mass_props(V, F)
    Vb = np.ascontiguousarray(V - c)
    Nb = face_normals(V, F)
    return Vb, Nb, np.linalg.inv(I / vol)


@njit(parallel=True, cache=True)
def basin_pts(Vb, Nb, Ibinv, q0, x0, v0, WP, e, mu, dt, tmax):
    """outcomes for a list of angular velocities WP (M, 3)."""
    M = WP.shape[0]
    out = np.zeros(M, np.int64)
    dummy = np.zeros((1, 7))
    for k in prange(M):
        f, t, n = throw(Vb, Nb, Ibinv, x0, q0, v0, WP[k].copy(), e, mu, dt, tmax, 0, dummy)
        out[k] = f
    return out
