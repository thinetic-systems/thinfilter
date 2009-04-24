
url="http://10.0.0.1:9090/stats/dfsfs/fdsfd2.ht/dsafa/fdsfs.html"

import re
print re.search('/([^/]+)/?$', url).group(1)

