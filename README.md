# Instagram 2 Events

This project implements a combination of existing software to scrape, analyze, and interpret Instagram posts and filter
out any events found.

This project heavily relies on Instaloader, EasyOCR, and Ollama. More details can be found in the **Acknowledgments**
section. We also direct you to our **License, Warranty and Disclaimer** sections at the bottom of this page.

This project was designed for use in conjunction with the
project [Bewegungskalender](https://0xacab.org/aktivistek/bewegungskalender).

## Implemented Specs & Features

- Scrape specified Instagram accounts and hashtags.
- Analyze images using OCR.
- Run specified LLMs on the captions and, optionally, OCR output of scraped and analyzed content.
- All steps of this process are saved in a `sync.pkl` file, and results are output to `.json` files in the corresponding
  posts directories.

## Acknowledgments

This software heavily relies on the amazing work of the maintainers and contributors of the following projects:

- [Instaloader](https://github.com/instaloader/instaloader)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [Ollama Python Library](https://github.com/ollama/ollama-python)
- [As well as Ollama](https://ollama.com/download)

We also refer you to the acknowledgment sections in the mentioned software repositories for further information.

## Setup and Usage

Make use to have python and uv installed. More details on https://docs.astral.sh/uv/
Also make sure you have ollama installed. More details on https://ollama.com/

### Setup

Install dependencies using `uv sync`.

Define accounts and hashtags to be scraped as environment variables. Separate each account/hashtag with a ',' and don't
include @ and # in the list. See the following example:

```
SCRAPE_ACCOUNTS=downloadme,alsodownloadme
SCRAPE_HASHTAGS=downloadme,alsodownloadme
```

Decide what LLMs to use. Download these with Ollama and define them in environment variables. The default values are:

```
MODEL_LARGE=gemma3:4b
MODEL_SMALL=deepseek-r1:8b
```

Optionally set up a login username and session file. See the [Instaloader Docs](https://instaloader.github.io/) for more
details on acquiring this session file. See the following example:

```
LOGIN_SESSION_FILE=session/session-youraccount
LOGIN_USERNAME=youraccount
```

For further environment variables and config, see the `config.py` file.

### Findings on Models

Based on limited testing, I have concluded that model sizes with parameter sizes of around **8b are the absolute minimum
required to obtain somewhat reliable results** for event data parsing. **More intelligent models with more than 15 or
30
significantly improves the
results** and should also allow for the adjustment of prompts with more details and compensations.

For classification however already smaller models such as `gemma3:4b` seem to be okay, however the basic classifier
proves to be very effective as well and I would actually recommend it over the llm based classifier.

### Usage

Scrape all content:

```uv run scraper.py```

(Optionally) Run OCR reader (Can optionally be run after classifier and with `OCR_ONLY_ON_AS_EVENT_CLASSIFIED` set to
true to only run ocr on "promising" posts):

```uv run ocr_reader.py```

Classify all posts (decides if post has data on events/dates):

```uv run classifier.py```

Run LLMs on content (Specify whether to use OCR results in environment variables):

```uv run interpreter.py```

## License and Warranty

Copyright (C) 2025 Jana Caroline Pasewalck

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not,
see <https://www.gnu.org/licenses/>.

## Ethical Disclaimer

This software is intended for use on publicly available data only, and we highly encourage asking for explicit
permission from any publisher's content you scrape or analyze using this and the underlying software.

We find it important to use AI responsibly. We condemn the current *unregulated* and *unethical* use of AI by
corporations. We believe in aiming for a decentralized and self-determined use of existing models to fight back against
corporations while emphasizing ethical concerns in how large language models were trained, created, and how they can be
used in damaging ways.

We especially condemn the non-consensual collection and analysis of any personal data.

For more information on LLMs, we are happy to refer you to [bits-und-baeume.org](https://bits-und-baeume.org/) and to
other amazing people working on this matter.

## Legal Disclaimer

While web scraping and interpretation of scraped data is legal, it is important to be aware of the legal limitations of
this freedom.

We refer to the legal regulations of the countries this software is published and used in, such as the GDPR for the
European Union.

This software and the bundled software are not designed, authorized, supported, affiliated, maintained, or endorsed by
Meta (Instagram). Use at your own risk.

This legal disclaimer is based on the following sources:

- https://legalclarity.org/is-data-scraping-illegal-the-law-explained/
- https://github.com/instaloader/instaloader?tab=MIT-1-ov-file





