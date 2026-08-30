import re
F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/queries.py"
t = open(F).read()

# backtick already done. Now fix if( ternaries that span newlines.
# Convert if( on sql to case when. Use a paren-matcher.
def find_paren(s, i):
    depth=0
    for j in range(i, len(s)):
        if s[j]=='(': depth+=1
        elif s[j]==')':
            depth-=1
            if depth==0: return j
    return -1

out=[]; i=0; conv=0
while i < len(t):
    # look for "if(" not part of a word (avoid builtin if statements)
    m = re.search(r'(?<![\w.])if\(', t[i:])
    if not m:
        out.append(t[i:]); break
    start = i + m.start()
    # skip python control 'if (' at start of line (indent + 'if ')
    pre = t[max(0,start-1):start]
    # determine if this is SQL if( by checking following content has comma-comma pattern
    end = find_paren(t, start)  # end of if(...)
    seg = t[start:end+1]
    # count top-level commas
    depth=0; commas=0
    for ch in seg[3:-1]:
        if ch=='(': depth+=1
        elif ch==')': depth-=1
        elif ch==',' and depth==0: commas+=1
    if commas>=2:
        # it's a ternary if(a,b,c) -> case when a then b else c end
        inner = seg[3:-1]
        # split on top-level commas
        parts=[]; d=0; cur=''
        for ch in inner:
            if ch=='(': d+=1; cur+=ch
            elif ch==')': d-=1; cur+=ch
            elif ch==',' and d==0: parts.append(cur.strip()); cur=''
            else: cur+=ch
        parts.append(cur.strip())
        if len(parts)==3:
            repl = "(case when %s then %s else %s end)" % (parts[0], parts[1], parts[2])
            out.append(t[i:start]); out.append(repl); i=end+1; conv+=1; continue
    # not a ternary, keep as-is
    out.append(t[i:start+3]); i=start+3
t="".join(out)
open(F,"w").write(t)
print("if-ternary conversions:", conv)
print("remaining `tab:", len(re.findall(r'`tab', t)), "ifnull:", t.count("ifnull("), "0000-00-00:", t.count("'0000-00-00'"))
