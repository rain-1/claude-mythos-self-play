import render_sub as R
h = R.build(8192, M=110, coral=(97, -70), fadelen=0.16, bl=0.32, wt=0.55, bombw=0.12,
            out='already_on_the_list_4096.png', final=(4096, 4096))
import json
c = h.certify()
c['coral_submarine'] = dict(a=97, b=-70, capture_time=h.capture_time(97, -70))
json.dump(c, open('already_on_the_list_cert.json', 'w'), indent=1)
print(json.dumps(c, indent=1))
