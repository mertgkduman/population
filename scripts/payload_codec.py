"""Lossless repeated-numeric-array packaging; no scientific rounding or lossy casts."""
import hashlib,json
def pack(value):
    pool=[];seen={};references=0
    def visit(x):
        nonlocal references
        if isinstance(x,list):
            if len(x)>=32 and all(v is None or isinstance(v,(int,float)) for v in x):
                raw=json.dumps(x,separators=(',',':'),allow_nan=False).encode();key=hashlib.sha256(raw).digest()
                if key not in seen:seen[key]=len(pool);pool.append(x)
                references+=1
                return {'$numeric_array':seen[key]}
            return [visit(v) for v in x]
        if isinstance(x,dict):return {k:visit(v) for k,v in x.items()}
        return x
    data=visit(value)
    return {'_encoding':'numeric-array-pool-v1','data':data,'arrays':pool}, {'references':references,'unique_arrays':len(pool)}

def unpack(value):
    if value.get('_encoding')!='numeric-array-pool-v1':return value
    def visit(x):
        if isinstance(x,dict):
            if list(x)==['$numeric_array']:return value['arrays'][x['$numeric_array']].copy()
            return {k:visit(v) for k,v in x.items()}
        if isinstance(x,list):return [visit(v) for v in x]
        return x
    return visit(value['data'])

JS_UNPACK="""function unpackPayload(p){if(p._encoding!=='numeric-array-pool-v1')return p;function v(x){if(Array.isArray(x))return x.map(v);if(x&&typeof x==='object'){if(Object.keys(x).length===1&&'$numeric_array' in x)return p.arrays[x.$numeric_array].slice();return Object.fromEntries(Object.entries(x).map(([k,y])=>[k,v(y)]))}return x}return v(p.data)}"""
