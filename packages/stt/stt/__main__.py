import json
from tempfile import NamedTemporaryFile

import requests
from speech_recognition import Recognizer, AudioFile


def bytes2audiodata(data):
    recognizer = Recognizer()
    with NamedTemporaryFile() as fp:
        fp.write(data)
        with AudioFile(fp.name) as source:
            audio = recognizer.record(source)
    return audio


class ChromiumSTT:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pfilter = False

        # no keys issued since at least march 9 2016
        # http://web.archive.org/web/20160309230031/http://www.chromium.org/developers/how-tos/api-keys
        # key scrapped from commit linked bellow, dated Jun 8, 2014
        # https://github.com/Uberi/speech_recognition/commit/633c2cf54466a748d1db6ad0715c8cbdb27dbb09
        # let's hope it just keeps on working!
        self.key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"

    def execute(self, audio, language):
        flac_data = audio.get_flac_data(
            convert_rate=None if audio.sample_rate >= 8000 else 8000,
            # audio samples must be at least 8 kHz
            convert_width=2  # audio samples must be 16-bit
        )

        params = {
            "client": "chromium",
            "lang": language,
            "key": self.key,
            "pFilter": int(self.pfilter)
        }
        sample_rate = str(audio.sample_rate)
        headers = {"Content-Type": "audio/x-flac; rate=" + sample_rate}
        url = "http://www.google.com/speech-api/v2/recognize"
        r = requests.post(url, headers=headers, data=flac_data, params=params)

        # weirdly this returns something like
        """
        {"result":[]}
        {"result":[{"alternative":[{"transcript":"Hello world","confidence":0.83848035},{"transcript":"hello hello"},{"transcript":"Hello"},{"transcript":"Hello old"},{"transcript":"Hello howdy"}],"final":true}],"result_index":0}
        """

        result = r.text.split("\n")[1]
        data = json.loads(result)["result"]
        if len(data) == 0:
            return ""
        data = data[0]["alternative"]

        if len(data) == 0:
            return ""

        # we arbitrarily choose the first hypothesis by default.
        # results seem to be ordered by confidence
        best_hypothesis = data[0]["transcript"]

        # if confidence is provided return highest conf
        candidates = [alt for alt in data if alt.get("confidence")]

        if len(candidates):
            best = max(candidates, key=lambda alt: alt["confidence"])
            best_hypothesis = best["transcript"]

        return best_hypothesis


def main(args):
    print(args)
    # stt = ChromiumSTT()
    lang = args.get("lang", "en-us").lower()
    # TODO - check format of args to see how audio is passed
    # audio = args.get("audio")
    # utt = stt.execute(bytes2audiodata()audio)
    return {
        'body': {
            'lang': lang,
            'text': str(args)
        }
    }
