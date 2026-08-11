# Embedding evaluation

MTEB asks whether an embedding model is strong on external benchmark tasks. The AcmeCloud retrieval benchmark and Ragas ask whether the embedding/retriever works for this application. Both are required.

Selection workflow: candidates → small MTEB retrieval benchmark → shortlist → AcmeCloud rank/recall benchmark → Ragas context precision/recall → latency and cost → production selection.

The Azure embedding deployment is exposed through a custom MTEB encoder because it is a hosted deployment, not a model in MTEB's registry. This custom boundary is labeled in code. The default external tasks are NFCorpus and SciFact to control expense. Add similarity, clustering, or classification only when the application needs them.

```bash
pip install -e '.[embeddings]'
AIQ_ALLOW_LIVE_MODEL_CALLS=true make test-embeddings
```

Compare at least Azure primary and a local sentence-transformer baseline where policy permits. Reject an embedding that looks competitive on MTEB but reduces application context recall.
