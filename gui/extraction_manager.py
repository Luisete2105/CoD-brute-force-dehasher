import multiprocessing as mp
from core.script_processor import ScriptProcessor
from datetime import datetime

class ExtractionManager:
    def __init__(self, log_queue, progress_queue):
        self.log_queue = log_queue
        self.progress_queue = progress_queue
        self.process = None
        self._is_processing = False
        self.result = None

    def start_extraction(self, folder, detected_game):
        if not folder:
            self.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No folder selected")
            return

        while not self.progress_queue.empty():
            try:
                self.progress_queue.get_nowait()
            except mp.queues.Empty:
                break

        self._is_processing = True
        self.progress_queue.put(0.0)
        self.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting extraction for {folder}")

        self.process = mp.Process(
            target=self._process_scripts_wrapper,
            args=(folder, detected_game, self.log_queue, self.progress_queue, self)
        )
        self.process.start()

    @staticmethod
    def _process_scripts_wrapper(folder, detected_game, log_queue, progress_queue, manager):
        processor = ScriptProcessor(
            log_file_path="debug.log",
            progress_queue=progress_queue
        )
        try:
            total, unhashed, hashed = processor.process_scripts(folder, detected_game)
            manager.result = (total, unhashed, hashed)
            progress_queue.put(100.0)
        except Exception as e:
            log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error during extraction: {str(e)}")

    def is_processing(self):
        if self.process and self.process.is_alive():
            return True
        if self._is_processing and self.result:
            total, unhashed, hashed = self.result
            self.log_queue.put(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Extraction complete: {total} words ({unhashed} unhashed, {hashed} hashed)"
            )
            self.result = None
        self._is_processing = False
        return False