import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract bin file.')
    parser.add_argument('-i','--input', required=True, type=str, help='Input file')
    parser.add_argument('-offset', required=True, type=str, help='Start offset')
    parser.add_argument('-size', required=True, type=str, help='size')
    parser.add_argument('-o','--output', required=True, type=str, help='Output file')
    args = parser.parse_args()

    Start=int(args.offset,0)
    End=Start+int(args.size,0)
    EndHexStr=str(hex(End))
    print (f'Input File: {args.input}')
    print (f'Extract Start {args.offset} to {EndHexStr}')
    print (f'Length: {args.size}')
    print (f'Output File: {args.output}')

    with open(args.input, 'rb') as f:
        s = f.read()
    Start=int(args.offset,0)
    End=Start+int(args.size,0)
    BinBuffer=s[Start:End]

    f=open(args.output,'wb')
    f.write(BinBuffer)
    f.close