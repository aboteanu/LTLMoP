from LTLFormula import LTLFormula
import sys
import subprocess

def diffLTLSpecs( filename1, filename2 ):
    """
    Parse two LTL files into trees and reprint them for comparison
    """

    spec1_assumptions, spec1_guarantees = LTLFormula.fromLTLFile( filename1 )
    spec2_assumptions, spec2_guarantees = LTLFormula.fromLTLFile( filename2 )

    default_stdout = sys.stdout
    outfilename1 = '_'+filename1
    outfilename2 = '_'+filename2
    outfile1 = open(outfilename1, 'wt')
    outfile2 = open(outfilename2, 'wt')

    # redirect stdout for first print
    sys.stdout = outfile1
    spec1_assumptions.printTree()
    print '\n'
    spec1_guarantees.printTree()

    # redirect stdout for second print
    sys.stdout = outfile2
    spec2_assumptions.printTree()
    print '\n'
    spec2_guarantees.printTree()

    # reset stdout
    sys.stdout = default_stdout

    outfile1.close()
    outfile2.close()

    diff_command = ["diff", outfilename1, outfilename2]
    diff_process = subprocess.Popen(diff_command)
   
if __name__=="__main__":
    assert len(sys.argv)==3, 'give two ltl file names as input'
    f1 = sys.argv[1]
    f2 = sys.argv[2]
    diffLTLSpecs( f1, f2 ) 
