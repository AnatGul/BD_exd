# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main entry point for Bangladesh Export Declaration Processor

Usage:
    python exdBD.py                           # Process all files in default input directory
    python exdBD.py <input_dir>            # Process files in specified directory
    python exdBD.py <input_file>         # Process single file
    python exdBD.py -o <output_dir>       # Specify output directory
    python exdBD.py --test                # Run test mode

Examples:
    python exdBD.py data/input
    python exdBD.py D:\\scans\\EXD AFL-GJ-2026-005-M.jpg
    python exdBD.py D:\\scans -o D:\\output
"""
import os
import sys
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import BangladeshExportProcessor, process_directory, process_file


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Bangladesh Export Declaration Processor - OCR + Translation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('input', nargs='?', help='Input file or directory')
    parser.add_argument('-o', '--output', help='Output directory or file')
    parser.add_argument('--test', action='store_true', help='Run test mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Determine paths
    if args.test or not args.input:
        # Default to working directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(script_dir)
        
        input_dir = os.path.join(base_dir, 'data', 'input')
        output_dir = os.path.join(base_dir, 'data', 'output')
        
        if not os.path.exists(input_dir):
            # Use current directory
            input_dir = os.getcwd()
            output_dir = os.getcwd()
        
        print(f"Input directory: {input_dir}")
        print(f"Output directory: {output_dir}")
        
        # Get files
        test_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.pdf']:
            import glob
            test_files.extend(glob.glob(os.path.join(input_dir, ext)))
        
        if not test_files:
            print("No input files found")
            
            # Check working directory
            working_files = glob.glob(os.path.join(os.getcwd(), '*.jpg'))
            if working_files:
                print(f"Found files in current directory: {working_files}")
                input_dir = os.getcwd()
                output_dir = os.getcwd()
            else:
                print("No files found. Place scanned declarations in data/input directory")
                sys.exit(1)
        
        processor = BangladeshExportProcessor(input_dir, output_dir)
        
        if args.test:
            outputs = processor.process_all()
            print(f"\n=== Complete ===")
            print(f"Processed {len(outputs)} files")
        else:
            # Interactive mode
            if test_files:
                for f in test_files[:4]:  # Process up to 4 files
                    try:
                        output_path = processor.process_and_save(f)
                        print(f"Created: {output_path}")
                    except Exception as e:
                        print(f"Error: {e}")
    
    elif os.path.isdir(args.input):
        # Directory mode
        output_dir = args.output or args.input
        outputs = process_directory(args.input, output_dir)
        print(f"Processed {len(outputs)} files")
    
    elif os.path.isfile(args.input):
        # Single file mode
        if args.output:
            output_path = process_file(args.input, args.output)
        else:
            output_path = process_file(args.input)
        print(f"Created: {output_path}")
    
    else:
        print(f"Input not found: {args.input}")
        sys.exit(1)


if __name__ == '__main__':
    main()