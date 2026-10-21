import json
from pathlib import Path

index=65530
events=[]
for loop in range(12):
    if index % 5 == 0:
        events.append({'loop':loop,'index':index})
    index=(index+1)&0xffff
gaps=[b['loop']-a['loop'] for a,b in zip(events,events[1:])]
assert gaps == [5,1,5]
assert 8/8*336/2 == 168
assert 336/4 == 84 and 84 > 75
assert 336/7 == 48
assert 168_000_000//100-1 == 1_679_999
assert 168_000_000//1000-1 == 167_999
result={'index_events':events,'loop_gaps':gaps,'nominal_intervals_ms':[x*100 for x in gaps],'pll_check':'84 MHz exceeds 75 MHz specification; Q=7 gives 48 MHz','systick_check':'passed'}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
