from typing import Literal

from numpy.f2py.auxfuncs import throw_error

from tracker import use_tracker, PostTracker
from util.basic_classifier import classic_classifier
from util.config import INTERPRETER_CLASSIFIER_MODE, \
    RERUN_CLASSIFIER
from util.ollama_client import llm_classify


def main():
    with use_tracker() as sync_tracker:
        targets = []
        for post in sync_tracker.posts.values():
            if not post.classified or RERUN_CLASSIFIER:
                targets.append(post)
        count = 0
        for post in targets:
            count += 1
            print(f"Post {count} / {len(targets)}")
            post.classified_as_event = classifier(post).is_event
            post.classified = True


class ClassifierPassResult:
    def __init__(self, mode):
        self.mode = mode

    def run(self, post: PostTracker):
        if self.mode == "llm":
            self.is_event = llm_classify(post)
            self.confidence = "Ok"
        elif self.mode == "basic":
            self.confidence = "Ok"
            self.is_event = classic_classifier(post)
        self.is_run = True
        return self

    is_run: bool = False
    is_event: bool
    confidence: str
    mode: Literal["basic", "llm-small", "llm-large"]


class ClassifierResult:
    is_event: bool = False
    passes: list[ClassifierPassResult]

    def __init__(self, passes):
        self.passes = passes

    def run(self, post: PostTracker):
        print(f"Start classification for {post.media_id}")
        for _ in self.passes:
            _.run(post)
            self.is_event = _.is_event
            print(f" Classification for {post.media_id} with {_.mode} is: {_.is_event} with confidence: {_.confidence}")
            if not _.is_event:
                print(f"Final classification for {post.media_id}: {self.is_event}")
                return self
        print(f"Final classification for {post.media_id}: {self.is_event}")
        return self


def classifier(post) -> ClassifierResult | None:
    if INTERPRETER_CLASSIFIER_MODE == "basic":
        return ClassifierResult([ClassifierPassResult("basic")]).run(post)
    elif INTERPRETER_CLASSIFIER_MODE == "llm":
        return ClassifierResult([ClassifierPassResult("llm")]).run(post)
    elif INTERPRETER_CLASSIFIER_MODE == "stacked":
        return ClassifierResult([ClassifierPassResult("basic"), ClassifierPassResult("llm")]).run(post)
    else:
        throw_error("No Interpreter Mode")


if __name__ == "__main__":
    main()
