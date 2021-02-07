import requests
from lxml import html


for i in range(1, 13):
    numstring = '0{}'.format(i) if i < 10 else str(i)
    url = 'http://web.archive.org/web/20081219085635/http://www.alc.co.jp/goi/svl_l{}_list.htm'.format(numstring)
    page = requests.get(url)
    tree = html.fromstring(page.content)
    containing_element = next(x for x in tree.xpath('//font') if len(x) > 900)
    entries = {x.tail.strip() for x in containing_element if x.tag == 'br'}
    if containing_element.text is not None:
        entries.add(containing_element.text.strip())
    assert(len(entries) == 1000)
    with open('svl_lvl_{}.txt'.format(i), 'w+') as f:
        f.writelines(x+'\n' for x in entries)


