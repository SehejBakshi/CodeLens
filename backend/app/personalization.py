import sqlite3
from sentence_transformers import SentenceTransformer, util

class PersonalizationStore:
    def __init__(self, db_path="personal.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS examples (code TEXT, feedback TEXT)")
        #self.create_table()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    # def create_table(self):
    #     with self.conn:
    #         self.conn.execute('''
    #             CREATE TABLE IF NOT EXISTS examples (
    #                 id INTEGER PRIMARY KEY,
    #                 code TEXT,
    #                 feedback TEXT,
    #                 embedding BLOB
    #             )
    #         ''')

    def add_example(self, code: str, feedback: str):
        self.conn.execute("INSERT INTO examples (code, feedback) VALUES (?,?)", (code, feedback))
        self.conn.commit()
        # embedding = self.model.encode(code)
        # with self.conn:
        #     self.conn.execute('''
        #         INSERT INTO examples (code, feedback, embedding) VALUES (?, ?, ?)
        #     ''', (code, feedback, embedding.tobytes()))

    def get_examples(self, code: str, k: int =3):
        cursor = self.conn.execute("SELECT code, feedback FROM examples")
        rows = cursor.fetchall()
        if not rows:
            return []

        codes, feedbacks = zip(*rows)
        embeddings = self.model.encode(list(codes), convert_to_tensor=True)
        query_emb = self.model.encode(code, convert_to_tensor=True)
        scores = util.cos_sim(query_emb, embeddings)[0]
        topk = scores.topk(k)
        result = [(codes[i], feedbacks[i]) for i in topk.indices.tolist()]
        return result
        # query_embedding = self.model.encode(code)
        # cursor = self.conn.cursor()
        # cursor.execute('SELECT id, code, feedback, embedding FROM examples')
        # examples = []
        # for row in cursor.fetchall():
        #     ex_id, ex_code, ex_feedback, ex_embedding_blob = row
        #     ex_embedding = np.frombuffer(ex_embedding_blob, dtype=np.float32)
        #     sim = util.cos_sim(query_embedding, ex_embedding).item()
        #     examples.append((sim, ex_code, ex_feedback))
        # examples.sort(reverse=True, key=lambda x: x[0])
        # return [(ex_code, ex_feedback) for _, ex_code, ex_feedback in examples[:k]]