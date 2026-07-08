import fitz

# Create a sample PDF to test get_text behavior
doc = fitz.open()
page = doc.new_page()
page.insert_text((50, 50), "Hello World", fontsize=12)
page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(40, 40, 100, 60), "uri": "http://example.com"})

for link in page.get_links():
    rect = link.get("from")
    print("rect:", rect)
    text = page.get_text("text", clip=rect)
    print("type:", type(text))
    print("text:", repr(text))
