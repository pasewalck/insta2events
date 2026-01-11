from numpy.f2py.auxfuncs import throw_error

from tracker import use_tracker
from util.basic_classifier import classic_classifier
from util.config import INTERPRETER_CLASSIFIER_MODE, \
    RERUN_CLASSIFIER
from util.llm import llm_classify


def main():
    with use_tracker() as sync_tracker:

        for post in sync_tracker.posts.values():
            if not post.classified or RERUN_CLASSIFIER:
                post.classified_as_event = classifier(post)
                print(f"Classification for {post.media_id}: {post.classified_as_event}")
                post.classified = True


def classifier(post):
    if INTERPRETER_CLASSIFIER_MODE == "basic":
        return classic_classifier(post)
    elif INTERPRETER_CLASSIFIER_MODE == "llm":
        llm_eval = llm_classify(post)
        print(f"LLM: {llm_eval}")
        return llm_eval["is_event"]
    else:
        throw_error("No Interpreter Mode")


if __name__ == "__main__":
    main()
