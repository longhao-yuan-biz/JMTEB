from __future__ import annotations

import json
from abc import ABC, abstractmethod

import datasets
import smart_open
from loguru import logger
from pydantic.dataclasses import dataclass


@dataclass
class RetrievalQuery:
    query: str
    relevant_docs: list[str | int]


@dataclass
class RetrievalDoc:
    id: str | int
    text: str


class RetrievalQueryDataset(ABC):
    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __getitem__(self, idx) -> RetrievalQuery:
        pass


class RetrievalDocDataset(ABC):
    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __getitem__(self, idx) -> RetrievalDoc:
        pass


class HfRetrievalQueryDataset(RetrievalQueryDataset):
    def __init__(
        self,
        path: str,
        split: str,
        name: str | None = None,
        query_key: str = "query",
        relevant_docs_key: str = "relevant_docs",
    ):
        self.dataset = datasets.load_dataset(path, split=split, name=name, trust_remote_code=True)
        self.query_key = query_key
        self.relevant_docs_key = relevant_docs_key

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx) -> RetrievalQuery:
        relevant_docs = self.dataset[idx][self.relevant_docs_key]
        if not isinstance(relevant_docs, list):
            relevant_docs = [relevant_docs]

        return RetrievalQuery(query=self.dataset[idx][self.query_key], relevant_docs=relevant_docs)


class JsonlRetrievalQueryDataset(RetrievalQueryDataset):
    def __init__(
        self,
        filename: str,
        query_key: str = "query",
        relevant_docs_key: str = "relevant_docs",
    ):
        self.dataset: datasets.Dataset = datasets.load_dataset("json", data_files=filename)["train"]
        self.query_key = query_key
        self.relevant_docs_key = relevant_docs_key

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx) -> RetrievalQuery:
        relevant_docs = self.dataset[idx][self.relevant_docs_key]
        if not isinstance(relevant_docs, list):
            relevant_docs = [relevant_docs]

        return RetrievalQuery(query=self.dataset[idx][self.query_key], relevant_docs=relevant_docs)


class HfRetrievalDocDataset(RetrievalDocDataset):
    def __init__(self, path: str, split: str, name: str | None = None, id_key: str = "docid", text_key: str = "text"):
        logger.info(f"Loading dataset {path} (name={name}) with split {split}")
        self.dataset = datasets.load_dataset(path, split=split, name=name, trust_remote_code=True)
        self.id_key = id_key
        self.text_key = text_key

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx) -> RetrievalDoc:
        return RetrievalDoc(id=self.dataset[idx][self.id_key], text=self.dataset[idx][self.text_key])


class JsonlRetrievalDocDataset(RetrievalDocDataset):
    def __init__(self, filename: str, id_key: str = "docid", text_key: str = "text"):
        logger.info(f"Loading dataset from {filename}")
        with smart_open.open(filename, "r", encoding="utf-8", errors="ignore") as fin:
            corpus = [json.loads(line.strip()) for line in fin.readlines()]
        self.dataset = corpus
        self.id_key = id_key
        self.text_key = text_key

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx) -> RetrievalDoc:
        return RetrievalDoc(id=self.dataset[idx][self.id_key], text=self.dataset[idx][self.text_key].strip())
