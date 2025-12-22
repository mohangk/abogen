import sys
import os
import argparse
import signal
import time
import logging
import tempfile
from abogen.engine import ConversionEngine
from abogen.book_parser import get_book_parser
from abogen.utils import load_numpy_kpipeline, prevent_sleep_start, prevent_sleep_end, load_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class AbogenCLI:
    def __init__(self, args):
        self.args = args
        self.engine = None
        
        # Setup signal handling for graceful exit
        signal.signal(signal.SIGINT, self.handle_sigint)

    def handle_sigint(self, signum, frame):
        print("\nInterrupted by user. Stopping...")
        if self.engine:
            self.engine.cancel()
        sys.exit(1)

    def start(self):
        try:
            self.run_conversion()
        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

    def log_callback(self, msg):
        if isinstance(msg, tuple):
            text, _ = msg
            print(text)
        else:
            print(msg)

    def progress_callback(self, value, etr):
        # Simple progress bar
        sys.stdout.write(f"\rProgress: {value}% - {etr}")
        sys.stdout.flush()

    def finished_callback(self, result, output_path):
        prevent_sleep_end()
        # Clean up temp file
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
            try:
                os.unlink(self.temp_file.name)
            except Exception:
                pass
                
        print("\nDone!")
        if isinstance(result, tuple):
            msg, _ = result
            logger.info(msg)
        else:
            logger.info(result)
            
        if not output_path:
             logger.error("Conversion failed.")
             sys.exit(1)
        
        # We don't exit here because run_conversion returns, and main exits.
        # But ConversionEngine.run() calls this callback.
        # Since run() is synchronous, we can just return.

    def run_conversion(self):
        input_file = self.args.input
        output_dir = self.args.output
        
        if not os.path.exists(input_file):
            logger.error(f"Input file not found: {input_file}")
            sys.exit(1)

        logger.info(f"Processing: {input_file}")
        
        # Parse book
        try:
            parser = get_book_parser(input_file)
            content_texts, content_lengths = parser.process_content()
            chapters = parser.get_chapters()
            
            total_chars = sum(content_lengths.values())
            logger.info(f"Found {len(chapters)} chapters, {total_chars} characters.")
            
            # Create a temporary file with the formatted text
            formatted_text = parser.get_formatted_text()
            self.temp_file = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False, suffix='.txt')
            self.temp_file.write(formatted_text)
            self.temp_file.close()
            logger.info(f"Prepared temporary processing file: {self.temp_file.name}")
            
        except Exception as e:
            logger.error(f"Failed to parse book: {e}")
            sys.exit(1)

        # Load Kokoro
        logger.info("Loading AI models...")
        np_module, kpipeline_class = load_numpy_kpipeline()
        
        # Prepare conversion engine
        voice_formula = self.args.voice
        lang_code = self.args.lang
        speed = self.args.speed
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        prevent_sleep_start()
        
        self.engine = ConversionEngine(
            file_name=self.temp_file.name,
            lang_code=lang_code,
            speed=speed,
            voice=voice_formula,
            save_option="Create a folder", # Force folder creation for CLI
            output_folder=output_dir,
            subtitle_mode="Sentence", # TODO: Add subtitle support to CLI args
            output_format="m4b", # TODO: Add format support to CLI args
            np_module=np_module,
            kpipeline_class=kpipeline_class,
            start_time=time.time(),
            total_char_count=total_chars,
            use_gpu=True, # Default to GPU if available
            from_queue=True, # Treat as queue to avoid GUI popups logic
            save_base_path=input_file,
            log_callback=self.log_callback,
            progress_callback=self.progress_callback,
            finished_callback=self.finished_callback
        )
        
        self.engine.run()

def main():
    parser = argparse.ArgumentParser(description="Abogen Headless CLI")
    parser.add_argument("--input", "-i", required=True, help="Input file (epub, pdf, md)")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    parser.add_argument("--voice", "-v", default="af_heart", help="Voice code (default: af_heart)")
    parser.add_argument("--lang", "-l", default="a", help="Language code (default: a)")
    parser.add_argument("--speed", "-s", type=float, default=1.0, help="Speed factor (default: 1.0)")
    
    args = parser.parse_args()
    
    cli = AbogenCLI(args)
    cli.start()

if __name__ == "__main__":
    main()
