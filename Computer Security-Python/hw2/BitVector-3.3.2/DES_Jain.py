#!/usr/bin/env/python

### hw2_starter.py

import sys
from BitVector import *
from random import randint
from Average_Jain import diffusion_or_confusion
import copy
################################   Initial setup  ################################

# Expansion permutation (See Section 3.3.1):
expansion_permutation = [31, 0, 1, 2, 3, 4, 3, 4, 5, 6, 7, 8, 7, 8, 
9, 10, 11, 12, 11, 12, 13, 14, 15, 16, 15, 16, 17, 18, 19, 20, 19, 
20, 21, 22, 23, 24, 23, 24, 25, 26, 27, 28, 27, 28, 29, 30, 31, 0]

# P-Box permutation (the last step of the Feistel function in Figure 4):
p_box_permutation = [15,6,19,20,28,11,27,16,0,14,22,25,4,17,30,9,
1,7,23,13,31,26,2,8,18,12,29,5,21,10,3,24]

# Initial permutation of the key (See Section 3.3.6):
key_permutation_1 = [56,48,40,32,24,16,8,0,57,49,41,33,25,17,9,1,58,
50,42,34,26,18,10,2,59,51,43,35,62,54,46,38,30,22,14,6,61,53,45,37,
29,21,13,5,60,52,44,36,28,20,12,4,27,19,11,3]

# Contraction permutation of the key (See Section 3.3.7):
key_permutation_2 = [13,16,10,23,0,4,2,27,14,5,20,9,22,18,11,3,25,
7,15,6,26,19,12,1,40,51,30,36,46,54,29,39,50,44,32,47,43,48,38,55,
33,52,45,41,49,35,28,31]

# Each integer here is the how much left-circular shift is applied
# to each half of the 56-bit key in each round (See Section 3.3.5):
shifts_key_halves = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1] 




###################################   S-boxes  ##################################

# Now create your s-boxes as an array of arrays by reading the contents
# of the file s-box-tables.txt:
with open('s-box-tables.txt') as f:
    arrays = []
    for line in f:
        if len(line) > 4:
            arrays.append(line.split()) #appending each line across all the s-tables to arrays 

s_box = []
for i in range(0,32,4):                #now making 8 s-tables out of the 'arrays' array
    s_box.append([arrays[k] for k in range(i, i+4)]) # S_BOX

f.close()


#######################  Get encryption key from user  ###########################

def get_encryption_key(): # key                                                              
    ## ask user for input
    #f = open("key.txt","r")
    key = raw_input("\nEnter 8 byte key: ") 
    ## make sure it satisfies any constraints on the key
    while not len(key) == 8:
        key = raw_input("\nInvalid key length! Re-enter 8 byte key: ")
    print 'You have provided an appropriate key.'    
    ## next, construct a BitVector from the key    
    user_key_bv = BitVector(textstring=key)   
    key_bv = user_key_bv.permute(key_permutation_1)     ## permute() is a BitVector function 
    
    ##using given key_permutation_1 vector to permute the input key. This is the first step to obtain a 48 bit round key from the 56 bit key input by the user.
    return key_bv


################################# Generating round keys  ########################
def extract_round_key( nkey ): # round key                                                   
    round_key = []    
    for i in range(16):
         [left,right] = nkey.divide_into_two()   ## divide_into_two() is a BitVector function
         left << shifts_key_halves[i]  #bit shifting by 1 or 2, the bits of the two halves of the input key
         right << shifts_key_halves[i]
         nkey = left + right
         round_key.append(nkey.permute(key_permutation_2)) #56 bit key -> 48 bit key using key_perm_2
    return round_key


########################## encryption and decryption #############################
def des(encrypt_or_decrypt, input_file, output_file, key ):
    new_bv = BitVector(size=64)
    new_bv1 = BitVector(size=64)
    bv = BitVector( filename = input_file )
    FILEOUT = open( output_file, 'w' )
    FILE = open("out1.txt",'w')
    count=0 ## counts number of times the while loop runs
    sum = 0   ## sums number of bits changed across all the blocks 
    sum1 = 0   ## sums number of bits changed across all the blocks->confusion

    while(bv.more_to_read):
        bitvec = bv.read_bits_from_file( 64 )   ## assumes that your file has an integral    
        bitvec.pad_from_right(64 - len(bitvec))  ## multiple of 8 bytes. If not, you must pad it.
        [LE, RE] = bitvec.divide_into_two()

        ### diffusion ###
        bit = randint(0,31) #generates index of the random bit to be changed
        diff_bv = RE.deep_copy() #new bitvector generated to measure diffusion

        if diff_bv[bit] == 0:
            diff_bv[bit] = 1
        else:
            diff_bv[bit] = 0
        ######################

        ### confusion ###
        bit1 = randint(0,47)
        diff_key = key.deep_copy()

        if diff_key[bit1] == 0:
            diff_key[bit1] = 1
        else:
            diff_key[bit1] = 0
        ######################

        rkey = extract_round_key(key)
        rkey1 = extract_round_key(diff_key)
        ## generating different bitvector accounting confusion and diffusion
        new_bv = diffusion_or_confusion(diff_bv, LE,encrypt_or_decrypt,rkey,s_box)
        new_bv1 = diffusion_or_confusion(RE,LE,encrypt_or_decrypt,rkey1,s_box) 
        for i in range(16):
            ## write code to carry out 16 rounds of processing
            TMP = RE

            ## Expansion_permutation
            RE = RE.permute(expansion_permutation)
            # Get the order of key right
            if encrypt_or_decrypt == "encrypt":
                RE = RE ^ rkey[i]
            elif encrypt_or_decrypt == "decrypt":
                RE = RE ^ rkey[15 - i]
            ## Do the S_boxes subsititution
            k=0
            output = BitVector(size = 0)
            for ct in range(8):
                row = RE[k]*pow(2,1) + RE[k+5]*pow(2,0)
                col = RE[k+1]*pow(2,3) + RE[k+2]*pow(2,2)+ RE[k+3]*pow(2,1) + RE[k+4]*pow(2,0)                           
                sbox_val = s_box[ct][row][col]

                sbox_bv = BitVector(intVal = int(sbox_val), size = 4)
                output += sbox_bv
                k += 6
            ## Permutation with P-Box
            output = output.permute(p_box_permutation)

            ## XOR with original LE
            RE = LE ^ output
            LE = TMP
        ## Add RE and LE up
        bitvec = RE + LE
        new_bv ^= bitvec
        new_bv1 ^= bitvec
        sum += new_bv.count_bits()
        count += 1
        sum1 += new_bv1.count_bits()

        ## Output the encryption or decryption
        mytext = bitvec.get_text_from_bitvector()
        FILEOUT.write(mytext)
    
    print 'Average number of bits changed for diffusion is', sum/count
    print 'Average number of bits changed for confusion is', sum1/count
    FILEOUT.close()
    

#################################### main #######################################
def main():
    ## write code that prompts the user for the key
    ## and then invokes the functionality of your implementation

    ## get the key

    ## Ask for encryption or decryption
    mykey = get_encryption_key()
    
    ans = raw_input("\nDo you want to encrypt or decrypt? ")
    while True:
        if ans == "encrypt":
            inputfile = "message.txt"
            outputfile = "encrypted.txt"
            break
        elif ans == "decrypt":
            inputfile = "encrypted.txt"
            outputfile = "decrypted.txt"
        break

    des(ans, inputfile, outputfile, mykey)
 
if __name__ == "__main__":
    main()
