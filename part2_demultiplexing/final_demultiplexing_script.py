#!/usr/bin/env python

import statistics
import argparse
import gzip

#R1_file = "/home/ntran2/bgmp/Bi621/Multiplexing/1294_S1_L008_R1_001.fastq.gz"
#R2_file = "/home/ntran2/bgmp/Bi621/Multiplexing/1294_S1_L008_R2_001.fastq.gz"
#R3_file = "/home/ntran2/bgmp/Bi621/Multiplexing/1294_S1_L008_R3_001.fastq.gz"
#R4_file = "/home/ntran2/bgmp/Bi621/Multiplexing/1294_S1_L008_R4_001.fastq.gz"

indexes = "/projects/bgmp/shared/2017_sequencing/indexes.txt"

def get_arguements():
    ```This function handles all argparse agruements i.e, specifying files, average quality score per record```
    parser = argparse.ArgumentParser(description="reading in different files & specifying quality cutoff")
    parser.add_argument("-a", "--R1_file", help="this argument specifies the R1 file", type =str, required=True)
    parser.add_argument("-b", "--R2_file", help="this argument specifies the R2 file", type =str, required=True)
    parser.add_argument("-c", "--R3_file", help="this argument specifies the R3 file", type =str, required=True)
    parser.add_argument("-d", "--R4_file", help="this argument specifies the R4 file", type =str, required=True)
    parser.add_argument("-q", "--avg_qscore", help="this argument specifies the quality score cut off", type =int, required=True)
    return parser.parse_args()

args=get_arguements()
a=args.R1_file
b=args.R2_file
c=args.R3_file
d=args.R4_file
q=args.avg_qscore


def convert_phred(letter):
```convert ascii characters to q score```
    return (ord(letter)) -33

def get_barcodes():
```opens the files containing the known barcodes, selects the column containing barcodes and stores it into a list```
    with open(indexes, "rt") as fh:
        known_barcodes = []
        next(fh)
        for line in fh:
            #splits elements in between spaces into a list
            line_split = line.split()
            #select the element containing the known_barcodes
            known_barcodes.append(line_split[4])
    return(known_barcodes)

def reverse_complement(seq):
```This functions reads in a index sequence or string and returns the reverse complement based on the critirion in the complement{} dictionary```
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'N': 'N'}

    bases = list(seq)
    bases = reversed([complement.get(base,base) for base in bases])
    bases = ''.join(bases)

    return bases



def get_Ns(seq_line):
```This function reads in a string from an indexes's sequence line and checks for Ns. If there is an "N" in seq line, the function returns True``
    #after reading in each basepair in the indexes' seq line, the basepairs are stored in the seq_line[] list for comparison
    seq_list = []

    #print(seq_line)
    LN = 0
    for i in seq_line:
        LN+=1
        if "N"  in seq_line:
            return True
            #return print("There's Ns in this quality line")

#this
qual_cutoff = q

def avg_qscore(qual_line):
```This function takes in the quality line of the BIOLOGICAL READS (R1 OR R4), adds quality score of each bp, returns mean. In downstream comparison: if mean qscore does not meet qscore cut off --> omit```

    LN =0
    q_list =[]
    score_list = []
    #quality score cut off set to
    qual_cutoff = 28
    for bp in qual_line:
        q_list.append(bp)
        #print(q_list)
        results = convert_phred(bp)
        #print(bp)
        score_list.append(results)
        LN +=1
    return statistics.mean(score_list)

def index_qual_per_base(index_qual_line):
```This function reads in the seq line of the indexes looks that the quality of each base pair and stores it into a list for comparison. If any nucleotide has a qscore lower than 20, return true ```
    LN = 0
    q_list = []
    scores_list = []
    index_qual_cutoff = 20
    for bp in index_qual_line:
        q_list.append(bp)
        results = convert_phred(bp)
        scores_list.append(results)
        LN += 1
    for any_bp in scores_list:
        if any_bp < index_qual_cutoff:
            return True


def write_to_file(file, record_list, barcode1, barcode2):
```this function write to file whenever a condition is met. Takes in 4 parameters: the file name, the 4 line record, R2's barcode and R3's barcode.```
    with open(file, "a") as file_out:
        header_line = record_list[0] + "_" + barcode1 + "_" + barcode2
        file_out.write(header_line + "\n")
        file_out.write(record_list[1] + "\n")
        file_out.write(record_list[2] + "\n")
        file_out.write(record_list[3] + "\n")
        file_out.close()


#these variables are initiated as counters to keep track of the occurances of dual matched, index hopped, or low qual observed
indexhopped_counter = 0
dual_matched_counter = 0
R1_lowqual = 0
R4_lowqual = 0

#opening R1,R2,R3, R4 and storing them into their respective file handles
with gzip.open(a, "rt") as R1, gzip.open(b, "rt") as R2, gzip.open(c, "rt") as R3, gzip.open(d, "rt") as R4:
    i = 0

    #storing file names of the four files into a list
    list_of_fh = [R1, R2, R3, R4]

    #calling the get_barcodes() function to retrieve the known barcode list
    barcode_list = get_barcodes()
    #unused variable: in_list
    in_list = False
    #empty list initiated for the purpose of storing matched indexes in a list, in downstream comparison, this list will be used to count the number of observed barcode occurances
    dual_matched_list =[]

    LN = 0
    while True:
        #Initiatizing empty list to store a single record from each file
        R1_rec = []
        R2_rec = []
        R3_rec = []
        R4_rec = []
        #don't forget to reset i to zero here...helps iterate through each record
        i = 0
        while i < 4:

            file_handle = list_of_fh[i]
            line1 = file_handle.readline()
            line2 = file_handle.readline()
            line3 = file_handle.readline()
            line4 = file_handle.readline()
            #rstrip removes the tailing "\n"
            if i == 0:
                R1_rec.append(line1.rstrip('\n'))
                R1_rec.append(line2.rstrip('\n'))
                R1_rec.append(line3.rstrip('\n'))
                R1_rec.append(line4.rstrip('\n'))
                #print(R1_rec)


            if i == 1:
                R2_rec.append(line1.rstrip('\n'))
                R2_rec.append(line2.rstrip('\n'))
                R2_rec.append(line3.rstrip('\n'))
                R2_rec.append(line4.rstrip('\n'))

            if i ==2:
                R3_rec.append(line1.rstrip('\n'))
                R3_rec.append(line2.rstrip('\n'))
                R3_rec.append(line3.rstrip('\n'))
                R3_rec.append(line4.rstrip('\n'))
            if i == 3:
                R4_rec.append(line1.rstrip('\n'))
                R4_rec.append(line2.rstrip('\n'))
                R4_rec.append(line3.rstrip('\n'))
                R4_rec.append(line4.rstrip('\n'))

            i+=1
        #method of breaking out of loop
        if len(R1_rec) < 4:
            break
        if line1 == "":
            break

        #checking quality conditions, if mean scores of the record is not meet, file out to undetermined
        #or
        #if statment files out if the index file R2 contains a quality score less than 20 in any base pair
        #or if there are any N's in the R2's sequence line
        if avg_qscore(R1_rec[3]) < qual_cutoff or index_qual_per_base(R2_rec[3]) == True or get_Ns(R2_rec[1]) == True or R2_rec[1] not in barcode_list:
            #this function call works, however, with every execution, the file will be appending the same record each time.
            write_to_file("undetermined_R1.txt", R1_rec, R2_rec[1], R3_rec[1])
            R1_lowqual +=1


        #quality accessment for R4 and R3:
        if avg_qscore(R4_rec[3]) < qual_cutoff or index_qual_per_base(R3_rec[3]) == True or get_Ns(R3_rec[1]) == True or R2_rec[1] not in barcode_list:
            #this function call works, however, with every execution, the file will be appending the same record each time.
            write_to_file("undetermined_R4.txt", R4_rec, R2_rec[1], R3_rec[1])
            R4_lowqual +=1


        #conditions to check if R2 index file contains a known index
        if R2_rec[1] in barcode_list and reverse_complement(R3_rec[1]) == R2_rec[1]:
            write_to_file(R2_rec[1]+"_R1.txt", R1_rec, R2_rec[1], R3_rec[1])
            write_to_file(R2_rec[1]+"_R4.txt", R4_rec, R2_rec[1], R3_rec[1])
            dual_matched_list.append(R2_rec[1])
            dual_matched_counter +=1

        #checking index-hopped conditions
        if R2_rec[1] in barcode_list and reverse_complement(R3_rec[1]) != R2_rec[1]:
            write_to_file("index-hopped_R1.txt", R1_rec, R2_rec[1], R3_rec[1])
            write_to_file("index-hopped_R4.txt", R4_rec, R2_rec[1], R3_rec[1])
            indexhopped_counter +=1

        #iterate to next set of records
        LN+=1

#printing summary statistics to Log.output.txt file
f = open("Log.output.txt",'w')
f.write("The following statistics was populated given the average quality score cutoff per record was set to: " + str(qual_cutoff) + " and the index quality score must be above 20 per base" + "\n" + "\n")
f.write("The total number of reads processed is: " + str(LN) + "\n")
f.write("The number of observed dual matched reads is: " + str(dual_matched_counter) + "\n")
f.write("The proportion of observed dual matched reads is: " + str((dual_matched_counter/LN) * 100) + "%" + "\n")
f.write("The number of observed index-hopped reads is: " + str(indexhopped_counter)+ "\n")
f.write("The proportion of observed index-hopped reads is: " + str((indexhopped_counter/LN) * 100)+ "%" +"\n")
f.write("The total number of reads filed to undetermined is: " + str(R1_lowqual)+ "\n")
f.write("The proportion of reads filed to undetermined is: " + str((R1_lowqual/LN) * 100)+ "%" + "\n")
f.write("---------------------------------------------------------------------------------------" + "\n")
#this for loop uses the set() method to search for unique known barcords and count occurances
for x in set(dual_matched_list):
            f.write("Index: {0} | Count: {1}".format(x,dual_matched_list.count(x)) + " | Proportion observed: " + str(("{1}".format(x,dual_matched_list.count(x)/LN * 100))) + "%" + "\n")

f.close()
