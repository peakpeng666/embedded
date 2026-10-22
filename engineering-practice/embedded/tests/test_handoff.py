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

    def test_hardware_readme_print_path(self):
        self.assertIn('../../verified-drawings/', (self.root / 'hardware/README.md').read_text())

    def package_inputs(self):
        for relative in ['output/pdf/Pandora_lceda-EDA_schematic-and-flowcharts.pdf', 'output/pdf/STM32L496_minimal-system-and-experiment-circuit_official-drawing.pdf', 'hardware/lceda/Pandora_L496_lceda-export.json', 'hardware/critical_review.md', 'hardware/lceda/verification-results.json', 'logs/windows_before_keil.json', 'logs/windows_after_keil.json']:
            p = self.root / relative
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('fixture')
        (self.root / 'hardware/sources').mkdir()
        video = self.root.parent / 'keil-board-demos'
        video.mkdir()
        for name in ['Windows-multi-tool-board-demo.mp4', 'Windows-multi-tool-board-demo.srt', 'lceda-EDA-schematic-review-demo.mp4']:
            (video / name).write_text('fixture')

    def test_package_git_failure_does_not_create_delivery(self):
        self.package_inputs()
        r = self.run_script('package_delivery.py')
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((self.root.parent / 'pandora-delivery').exists())

    def test_package_missing_tracked_source_preserves_delivery(self):
        self.package_inputs()
        subprocess.run(['git', 'init', str(self.base)], check=True, capture_output=True)
        source = self.root / 'lost.c'
        source.write_text('fixture')
        subprocess.run(['git', 'add', '.'], cwd=self.base, check=True, capture_output=True)
        source.unlink()
        dest = self.root.parent / 'pandora-delivery'
        dest.mkdir()
        (dest / 'sentinel').write_text('preserve')
        r = self.run_script('package_delivery.py')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('Missing source snapshot inputs', r.stderr)
        self.assertEqual([p.name for p in dest.iterdir()], ['sentinel'])

    def test_export_invalid_last_sheet_does_not_write(self):
        dest = self.root.parent / 'verified-drawings'
        edit = dest / 'editable-sources'
        edit.mkdir(parents=True)
        self.four_pages(edit / 'lceda-original-export.pdf')
        (edit / 'lceda-export-netlist.net').write_text('fixture')
        (dest / 'Pandora_L496_Verified.json').write_text(json.dumps({'title': 'Pandora_L496_Verified', 'schematics': [{'dataStr': {}}] * 3 + [{}]}))
        before = {p.relative_to(dest): p.read_bytes() for p in dest.rglob('*') if p.is_file()}
        r = self.run_script('export_verified_folder.py')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('Invalid four-sheet', r.stderr)
        self.assertFalse((self.root / 'logs').exists())
        self.assertFalse((self.root / 'output').exists())
        self.assertEqual(before, {p.relative_to(dest): p.read_bytes() for p in dest.rglob('*') if p.is_file()})

    def test_export_scalar_last_sheet_does_not_write(self):
        dest = self.root.parent / 'verified-drawings'
        edit = dest / 'editable-sources'
        edit.mkdir(parents=True)
        self.four_pages(edit / 'lceda-original-export.pdf')
        (edit / 'lceda-export-netlist.net').write_text('fixture')
        (dest / 'Pandora_L496_Verified.json').write_text(json.dumps({'title': 'Pandora_L496_Verified', 'schematics': [{'dataStr': {}}] * 3 + [{'dataStr': 42}]}))
        before = {p.relative_to(dest): p.read_bytes() for p in dest.rglob('*') if p.is_file()}
        r = self.run_script('export_verified_folder.py')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('Invalid four-sheet', r.stderr)
        self.assertFalse((self.root / 'logs').exists())
        self.assertFalse((self.root / 'output').exists())
        self.assertEqual(before, {p.relative_to(dest): p.read_bytes() for p in dest.rglob('*') if p.is_file()})

    def test_prepare_wrong_page_count_does_not_write(self):
        p = self.root / 'hardware/lceda/lceda-original-export.pdf'
        p.parent.mkdir(parents=True)
        with fitz.open() as doc:
            doc.new_page()
            doc.save(p)
        r = self.run_script('prepare_lceda_print.py')
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((self.root / 'output').exists())
        self.assertEqual([x.name for x in p.parent.iterdir()], [p.name])

    def test_scripts_parse(self):
        for name in ['prepare_lceda_print.py', 'export_verified_folder.py', 'package_delivery.py']:
            ast.parse((SOURCE / 'hardware' / name).read_text(encoding='utf-8'))
if __name__ == '__main__':
    unittest.main(verbosity=2)
