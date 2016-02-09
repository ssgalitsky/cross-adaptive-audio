from __future__ import absolute_import
import unittest
import settings
import sound_file
import template_handler
import csound_handler
import os
import time


class TestParallelizableCsound(unittest.TestCase):
    def setUp(self):
        settings.INPUT_DIRECTORY = 'test_audio'
        self.num_sounds = 100
        self.drums = sound_file.SoundFile('drums.wav')

    def test_serial_execution(self):
        self.start_time = time.time()

        for i in range(self.num_sounds):
            template = template_handler.TemplateHandler('templates/test_effect.csd.jinja2')
            duration = self.drums.get_duration()
            template.compile(
                sound_filename=self.drums.filename,
                ksmps=settings.CSOUND_KSMPS,
                duration=duration
            )

            csd_path = os.path.join(settings.CSD_DIRECTORY, 'test_effect_{}.csd'.format(i))
            template.write_result(csd_path)
            csound = csound_handler.CsoundHandler(csd_path)
            output_filename = self.drums.filename + '.test_processed_{}.wav'.format(i)
            csound.run(output_filename)

        print("Serial execution time for {0} sounds: {1} seconds".format(
            self.num_sounds,
            time.time() - self.start_time)
        )

    def test_parallel_execution(self):
        self.start_time = time.time()

        processes = []

        for i in range(self.num_sounds):
            template = template_handler.TemplateHandler('templates/test_effect.csd.jinja2')
            duration = self.drums.get_duration()
            template.compile(
                sound_filename=self.drums.filename,
                ksmps=settings.CSOUND_KSMPS,
                duration=duration
            )

            csd_path = os.path.join(settings.CSD_DIRECTORY, 'test_effect_{}.csd'.format(i))
            template.write_result(csd_path)
            csound = csound_handler.CsoundHandler(csd_path)
            output_filename = self.drums.filename + '.test_processed_{}.wav'.format(i)
            p = csound.run_async(output_filename)
            processes.append(p)

        for p in processes:
            p.wait()

        print("Parallel execution time for {0} sounds: {1} seconds".format(
            self.num_sounds,
            time.time() - self.start_time)
        )


if __name__ == '__main__':
    unittest.main()
