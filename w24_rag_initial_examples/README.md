# Week 24 - RAG with LangChain

## Context

I've been meaning to properly sit down with LangChain's RAG stack for a while. This week I finally did it, starting from the simplest possible pipeline and then layering in better retrieval.

## Overview

A notebook implementing a simple example of a RAG pipeline for querying any given PDF, running entirely locally. The pipeline uses a two-stage retrieval strategy: FAISS for fast approximate nearest-neighbour search followed by a cross-encoder reranker to improve precision before passing context to the LLM.

There is also a RAGAS evaluation section that uses Gemini to score the pipeline on faithfulness, answer relevancy, and context relevance, and plots the results of them.

## Topics Covered

- Document loading and chunking with LangChain (`PyMuPDFLoader`, `RecursiveCharacterTextSplitter`)
- Dense retrieval with **FAISS** and HuggingFace bi-encoder embeddings (`BGE-small-en-v1.5`)
- Cross-encoder reranking (`BGE-reranker-base`) via a custom `BaseRetriever` subclass
- Building LCEL chains with `RunnablePassthrough` and `StrOutputParser`
- Local LLM inference with `DeepSeek-R1-Distill-Qwen-1.5B` via `HuggingFacePipeline`
- Automated RAG evaluation with **RAGAS** (Faithfulness, Answer Relevancy, Context Relevance)

## Notes

- The PDF path in section 4 is hardcoded — update it to point to your own document.
- `faiss-cpu` is used here; swap for `faiss-gpu` if you have a CUDA-capable GPU for faster indexing on large corpora.
- The RAGAS evaluation block requires a `GOOGLE_API_KEY` in a `.env` file and the optional dependencies listed in `pyproject.toml`.
