from bs4 import BeautifulSoup


with open("throwaway.html", encoding='utf8') as f:
    html = f.read()

soup = BeautifulSoup(html, "html5lib")

if "Join to view full profiles for free" in html:
    print("ayy")