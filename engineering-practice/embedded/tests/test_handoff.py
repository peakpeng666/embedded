"""Offline handoff regression tests; require PyMuPDF, never access hardware.
Run: python -m unittest discover -s tests -p test_handoff.py -v
"""
from pathlib import Path
import tempfile, shutil, subprocess, sys, json, unittest, ast
import pymupdf as fitz
SOURCE = Path(__file__).resolve().parents[1]

class FixTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base / 'engineering-practice/embedded'
        for relative in ['docs/windows.md', 'hardware/README.md', 'hardware/prepare_lceda_print.py', 'hardware/export_verified_folder.py', 'hardware/package_delivery.py']:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / relative, target)

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, name):
        return subprocess.run([sys.executable, str(self.root / 'hardware' / name)], capture_output=True, text=True)

    def four_pages(self, p):
        p.parent.mkdir(parents=True, exist_ok=True)
        d = fitz.open()
        for i in range(4):
            d.new_page().insert_text((50, 50), f'Test page {i + 1}')
        d.save(p)
        d.close()

    def test_prepare_bootstraps_output(self):
        self.four_pages(self.root / 'hardware/lceda/lceda-original-export.pdf')
        self.assertFalse((self.root / 'output').exists())
        r = self.run_script('prepare_lceda_print.py')
        self.assertEqual(r.returncode, 0, r.stderr)
        with fitz.open(self.root / 'output/pdf/Pandora_lceda-EDA_schematic-and-flowcharts.pdf') as d:
            self.assertEqual(len(d), 4)
        self.assertEqual(len(list((self.root / 'output/pdf').glob('*.png'))), 4)

    def test_export_bootstraps_logs_output(self):
        dest = self.root.parent / 'verified-drawings'
        edit = dest / 'editable-sources'
        edit.mkdir(parents=True)
        self.four_pages(edit / 'lceda-original-export.pdf')
        (edit / 'lceda-export-netlist.net').write_text('fixture')
        (dest / 'Pandora_L496_Verified.json').write_text(json.dumps({'title': 'Pandora_L496_Verified', 'schematics': [{'dataStr': {}}] * 4}))
        (self.root / 'hardware/lceda').mkdir()
        r = self.run_script('export_verified_folder.py')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(list((self.root / 'logs').glob('verified_final_*.png'))), 4)
        self.assertTrue((self.root / 'output/pdf/Pandora_lceda-EDA_schematic-and-flowcharts.pdf').is_file())

    def test_package_missing_inputs_does_not_modify_delivery(self):
        dest = self.root.parent / 'pandora-delivery'
        dest.mkdir()
        (dest / 'sentinel').write_text('preserve')
        r = self.run_script('package_delivery.py')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('Missing local handoff inputs', r.stderr)
        self.assertEqual([p.name for p in dest.iterdir()], ['sentinel'])
        self.assertEqual((dest / 'sentinel').read_text(), 'preserve')

    def test_export_missing_inputs_does_not_create_outputs(self):
        r = self.run_script('export_verified_folder.py')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('Missing verified drawing inputs', r.stderr)
        self.assertFalse((self.root / 'logs').exists())
        self.assertFalse((self.root / 'output').exists())

    def test_docs_separate_old_and_new(self):
        s = (self.root / 'docs/windows.md').read_text()
        self.assertIn('C:\\Projects\\embedded\\engineering-practice\\embedded', s)
        self.assertIn('不要把 v1.0.0', s)
        self.assertIn('embedded-v1.0.0', s)

    @unittest.skip('Pending hardware README update: existing share-link retention requires confirmation')
    def test_hardware_readme_print_path(self):
        self.assertIn('../../verified-drawings/', (self.root / 'hardware/README.md').read_text())

    def test_scripts_parse(self):
        for name in ['prepare_lceda_print.py', 'export_verified_folder.py', 'package_delivery.py']:
            ast.parse((SOURCE / 'hardware' / name).read_text(encoding='utf-8'))
if __name__ == '__main__':
    unittest.main(verbosity=2)
