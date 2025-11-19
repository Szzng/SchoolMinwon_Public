from minwon.ai.common import get_chroma

col = get_chroma()

# 전체 document count
print("📌 총 문서 수:", col.count())

result = col.get()

ids = result.get("ids", [])
docs = result.get("documents", [])
metas = result.get("metadatas", [])

for i, doc, meta in zip(ids, docs, metas):
    print("\n==========================")
    print("📄 ID:", i)
    print("📘 요약 내용:", doc[:200], "..." if len(doc) > 200 else "")
    print("📝 메타데이터:", meta)
