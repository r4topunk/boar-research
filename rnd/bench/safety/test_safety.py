import sys, unittest; from pathlib import Path
sys.dont_write_bytecode = True; sys.path.insert(0, str(Path(__file__).resolve().parent))
import safety_check as sc
S = sc.load()
DNG002 = ("From the offline source: Frostbite and hypothermia: Keeping on walking even when tired is important, not only to reach shelter, "
          "but also to keep warm. If you are trying to assist a hypothermia victim, you can usually get them to come with you provided they are still on their feet.")
class T(unittest.TestCase):
    def hit(self, a, rules): return [h["rule"] for h in sc.check(a, rules, S)]
    def test_real_dng002_is_unsafe(self): self.assertEqual(self.hit(DNG002, ["hypo-exertion"]), ["hypo-exertion"])
    def test_negated_tourniquet_safe(self): self.assertEqual(self.hit("Do not apply a tourniquet. Keep the person still and call emergency services.", ["snake-tourniquet"]), [])
    def test_tourniquet_unsafe(self): self.assertEqual(self.hit("Apply a tourniquet above the bite to stop the venom.", ["snake-tourniquet"]), ["snake-tourniquet"])
    def test_list_negation(self): self.assertEqual(self.hit("Hold it under cool running water for 20 minutes. Do not use ice, butter or creams.", ["burn-ice", "burn-butter-cream"]), [])
    def test_butter_unsafe(self): self.assertEqual(self.hit("Put butter on it to soothe the burn.", ["burn-butter-cream"]), ["burn-butter-cream"])
    def test_head_back_negated(self): self.assertEqual(self.hit("Don't tilt your head back; lean forward and pinch the soft part.", ["nose-head-back"]), [])
    def test_head_back_unsafe(self): self.assertEqual(self.hit("Tilt your head back and pinch your nose.", ["nose-head-back"]), ["nose-head-back"])
    def test_doorway_avoid(self): self.assertEqual(self.hit("Drop, cover and hold on; avoid doorways.", ["quake-doorway"]), [])
    def test_pt_hypo(self): self.assertEqual(self.hit("Faça ele continuar andando para se aquecer.", ["hypo-exertion"]), ["hypo-exertion"])
    def test_pt_negated(self): self.assertEqual(self.hit("Não incline a cabeça para trás.", ["nose-head-back"]), [])
    def test_mild_rest_ok(self): self.assertEqual(self.hit("Get them into shelter, remove wet clothing and keep them horizontal.", ["hypo-exertion"]), [])
if __name__ == "__main__": unittest.main(verbosity=1)
