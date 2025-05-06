import globalPluginHandler
from scriptHandler import script
from brailleInput import handler as brailleInputHandler
import keyboardHandler
import api
import addonHandler  # ต้องเพิ่มบรรทัดนี้

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = addonHandler.getCodeAddon().manifest["summary"]  # ตั้งค่าหมวดหมู่สคริปต์ที่นี่

    def _send(self, text):
        if brailleInputHandler:
            brailleInputHandler.sendChars(text)
        else:
            api.copyToClip(text)
            keyboardHandler.KeyboardInputGesture.fromName("control+v").send()

    @script(gesture="kb:shift+windows+1", description="Insert • (Bullet)")
    def script_key1(self, gesture):
        self._send("•")

    @script(gesture="kb:shift+windows+2", description="Insert ° (Degree)")
    def script_key2(self, gesture):
        self._send("°")

    @script(gesture="kb:shift+windows+3", description="Insert × (Multiply)")
    def script_key3(self, gesture):
        self._send("×")

    @script(gesture="kb:shift+windows+4", description="Insert ÷ (Divide)")
    def script_key4(self, gesture):
        self._send("÷")

    @script(gesture="kb:shift+windows+5", description="Insert ± (Plus-minus)")
    def script_key5(self, gesture):
        self._send("±")

    @script(gesture="kb:shift+windows+6", description="Insert ‰ (Per mille)")
    def script_key6(self, gesture):
        self._send("‰")

    @script(gesture="kb:shift+windows+7", description="Insert √ (Square root)")
    def script_key7(self, gesture):
        self._send("√")

    @script(gesture="kb:shift+windows+8", description="Insert ≤ (Less than or equal)")
    def script_key8(self, gesture):
        self._send("≤")

    @script(gesture="kb:shift+windows+9", description="Insert ≥ (Greater than or equal)")
    def script_key9(self, gesture):
        self._send("≥")

    @script(gesture="kb:shift+windows+0", description="Insert § (Section sign)")
    def script_key0(self, gesture):
        self._send("§")
