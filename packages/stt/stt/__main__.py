from ovos_plugin_manager.stt import load_stt_plugin
from ovos_utils.log import LOG
from speech_recognition import Recognizer, AudioFile, AudioData
from ovos_stt_plugin_chromium import ChromiumSTT
from tempfile import NamedTemporaryFile

def bytes2audiodata(data):
    recognizer = Recognizer()
    with NamedTemporaryFile() as fp:
        fp.write(data)
        with AudioFile(fp.name) as source:
            audio = recognizer.record(source)
    return audio

  
def main(args):
  stt = ChromiumSTT()
  lang = args.get("lang", "en-us").lower()
  # TODO - check format of args to see how audio is passed
  #audio = args.get("audio")
  #utt = stt.execute(bytes2audiodata()audio)
  return {
    'body': {
      'args': str(args)
    }
  }
