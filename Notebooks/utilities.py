import random
import math
import numpy as np
import functools
import reedsolo

def OpenFile(file_path): 
    """ PROBABLY UNNECESSARY
    INPUT:
        filepath: path to the file
    OUTPUT:
        message: string containing the data of the file
    
    """
    with open(file_path, 'rb') as file:
        message = file.read()
    return message

def RandomizeMessage(segment, keygenseed = 7) -> bytearray:
    """Randomize all bytes to reduce homopolymers in the final DNA segments
    INPUT: 
        segment: original file, in bytearray format
        keygenseed: integer value of the seed to be used, default 7 
    OUTPUT:
        Randomize the message one byte at a time, using a known keygenseed.
    """
    randomized_segment = bytearray(len(segment))
    for i in range(len(segment)):
        random.seed(keygenseed)
        key = random.randint(0,255)
        keygenseed += 1 
        randomized_segment[i] = key ^ segment[i]
    return randomized_segment

def Segment(message) -> list:
    """ Segment the data into segments of 32 bytes, using padding to make sure the last segment has the correct lenght
    INPUT:
        message: string containing the data of the file
    OUTPUT:
        segment_list: list of binary strings
    """
    n=256
    ## add zero padding and amount of zero padding
    bits_to_add = n - (len(message) % n)
    message += '0'*(bits_to_add-8)
    padding_length = format(bits_to_add-1,'08b')
    message += padding_length
    
    ## segment data
    segments = [message[i:i+n] for i in range(0, len(message), n)]
    return segments

def Trits2DNA(base_3) -> str:
    meta_string=''

    A_dic = {'0':"C", '1': "G", '2':"T"}
    C_dic = {'0':"G", '1': "T", '2':"A"}
    G_dic = {'0':"T", '1': "A", '2':"C"}
    T_dic = {'0':"A", '1': "C", '2':"G"}

    for i in range(len(base_3)):
        if i == 0:
            nucleotide = A_dic[base_3[i]]
        elif meta_string[i-1] == 'A':
            nucleotide = A_dic[base_3[i]]
        elif meta_string[i-1] == 'C':
            nucleotide = C_dic[base_3[i]]
        elif meta_string[i-1] == 'G':
            nucleotide = G_dic[base_3[i]]
        elif meta_string[i-1] == 'T':
            nucleotide = T_dic[base_3[i]]
        meta_string = meta_string + nucleotide
    return meta_string

def CreateMetaStrand(number,eccbytes) -> str:
    """
    INPUT:
    number: number of segments the datafile is split in
    eccbytes: number of eccbytes added to the 
    OUTPUT:
    metasegment: segment containing metadata in DNA form
    """
    recognise_metadata = 'ACGTACGTACGTACGT'
    base_3 = np.base_repr(number,base=3)
    if len(base_3) > 16:
        print("Number of segments is too big")
    elif len(base_3) < 16:
        base_3 = (16-len(base_3))*'0' + base_3
    meta_string = Trits2DNA(base_3)
    metasegment = ''
    while len(metasegment) < 1:
        Random = RandomSegment(meta_string,eccbytes)
        metadata = recognise_metadata + meta_string + Random
        if CheckBiochemicalRequirements(metadata) == True:
            metasegment += metadata
    metasegment += metasegment
    return metasegment

def RandomSegment(meta_string,eccbytes) -> str:
    """
    INPUT:
    meta_string: string with the metadata in bases
    OUTPUT:
    random_segment: randomly created segment which can be added to the meta_string to form the final sequence if it passes biochemical restraints
                    segment is a palindrome to make it more recognisable
    """
    random_segment = ''
    j = int((56+2*eccbytes - len(meta_string))/2)
    for i in range(j):
        x = random.randint(1,4)
        if x == 1:
            random_segment += 'A'
        elif x == 2:
            random_segment += 'T'
        elif x == 3:
            random_segment += 'C'
        elif x == 4:
            random_segment += 'G'
    reverse = random_segment[::-1]
    if (j % 2) == 0:
        random_segment += reverse
    else:
        reverse = reverse[1:]
        random_segment += reverse
    return random_segment

def DNA2SegmentLength(s):
    base_3 = ''
    A_dic = {'C':"0", 'G': "1", 'T':"2"}
    C_dic = {'G':"0", 'T': "1", 'A':"2"}
    G_dic = {'T':"0", 'A': "1", 'C':"2"}
    T_dic = {'A':"0", 'C': "1", 'G':"2"}

    for i in range(len(s)):
        if i == 0:
            digit = A_dic[s[i]]
        elif s[i-1] == 'A':
            digit = A_dic[s[i]]
        elif s[i-1] == 'C':
            digit = C_dic[s[i]]
        elif s[i-1] == 'G':
            digit = G_dic[s[i]]
        elif s[i-1] == 'T':
            digit = T_dic[s[i]]
        base_3 = base_3 + digit
    segment_length=0
    for i in range(-1,-len(base_3)-1,-1):
        segment_length = segment_length + int(base_3[i])*3**(-i-1)
    
    return segment_length

def PalindromeSubStrs(s):
    """
    Function to find the longest palindrome in a string
    Input:
    s: string of nucleotides
    Output:
    palindrome: longest palindrome in s   
    """
    # Driver program
    # This code is contributed by BHAVYA JAIN and ROHIT SIKKA
    # https://www.geeksforgeeks.org/find-number-distinct-palindromic-sub-strings-given-string/

    m = dict()
    n = len(s)

    # table for storing results (2 rows for odd-
    # and even-length palindromes
    R = [[0 for x in range(n+1)] for x in range(2)]

    # Find all sub-string palindromes from the given input
    # string insert 'guards' to iterate easily over s
    s = "@" + s + "#"

    for j in range(2):
        rp = 0 # length of 'palindrome radius'
        R[j][0] = 0

        i = 1
        while i <= n:

            # Attempt to expand palindrome centered at i
            while s[i - rp - 1] == s[i + j + rp]:
                rp += 1 # Incrementing the length of palindromic
                        # radius as and when we find valid palindrome

            # Assigning the found palindromic length to odd/even
            # length array
            R[j][i] = rp
            k = 1
            while (R[j][i - k] != rp - k) and (k < rp):
                R[j][i+k] = min(R[j][i-k], rp - k)
                k += 1
            rp = max(rp - k, 0)
            i += k

    # remove guards
    s = s[1:len(s)-1]

    # Put all obtained palindromes in a hash map to
    # find only distinct palindrome
    m[s[0]] = 1
    for i in range(1,n):
        for j in range(2):
            for rp in range(R[j][i],0,-1):
                m[s[i - rp - 1 : i - rp - 1 + 2 * rp + j]] = 1
        m[s[i]] = 1


    # find longest palindrome and return this
    palindrome = max(m, key=len)
    return palindrome
    
def DecodeMetaStrand(metasegment, ecc_bytes) -> int:
    """
    Function to decode metasegments made by encode_metasegment
    INPUT:
    metasegment: segment returned after sequencing
    OUTPUT:
    number_off_segments: number of segments the file was divided in according to this segment, 
    this can be a single int or 2 integers based on if an error occured in one of the parts coding for the amount of segments
    """
    #check length
    if len(metasegment) == 144+ecc_bytes*4:
        s1 = metasegment[:len(metasegment)//2]
        s2 = metasegment[len(metasegment)//2:]
        #check if both halfs are the same
        if s1 == s2:
            s1 = s1.replace("ACGTACGTACGTACGT", "")
            #Find palindrome
            palindrome = PalindromeSubStrs(s1)
            #remove palindrome
            s1 = s1.replace(palindrome,"")
            #Decode amount of segments
            number_of_segments = int(DNA2SegmentLength(s1))
        
        else:
            s1 = s1[16:]
            s2 = s2[16:]
            palindrome_s1 = PalindromeSubStrs(s1)
            palindrome_s2 = PalindromeSubStrs(s2)
            if palindrome_s1 == palindrome_s2:
                s1 = s1.replace(palindrome_s1,"")  
                s2 = s2.replace(palindrome_s2,"") 
                if s1 == s2:
                    number_of_segments = int(DNA2SegmentLength(s1))
                else:
                    number_of_segments = []
                    number_of_segments.append(int(DNA2SegmentLength(s1)))
                    number_of_segments.append(int(DNA2SegmentLength(s2)))
            else:
                palindrome = [palindrome_s1, palindrome_s2]
                #print(palindrome)
                longest_palindrome = max(palindrome,key=len)
                #print(longest_palindrome)
                s1 = s1[:(len(s1)-len(longest_palindrome))]
                #print(s1)
                s2 = s2[:(len(s2)-len(longest_palindrome))]
                if s1 == s2:
                    number_of_segments = int(DNA2SegmentLength(s1))
                else:
                    number_of_segments = []
                    number_of_segments.append(int(DNA2SegmentLength(s1)))
                    number_of_segments.append(int(DNA2SegmentLength(s2)))
                    
    else:
        print('Segment length is not 152 bases!')
    return number_of_segments    
    
def IdealSoliton(K) -> list: 
    """ Generate a list of probalities of length K, following ideal soliton distribution
    INPUT:
        K: length of list
    OUTPUT:
        probabilities: list of probabilities following ideal soliton distribution
    """
    # initialize with the first two values, p(0) = 0 and p(1) = 1/K
    probabilities = [0, 1/K]
    # calculate the rest of the values using p(i) = 1/(i*(i-1))
    probabilities += [1/(i*(i-1)) for i in range(2, K+1)]
    return probabilities 

def RobustSoliton(K,c,delta) -> list:
    """ Generates a list of probalities of length K, following an robust soliton distribution with variables c and delta.
    INPUT:
        K: length of list
        c: value of c variable in distribution
        delta: value of delta variable in distribution
    OUTPUT:
        probabilities: list of probabilities following robust soliton distribution
    """
    #initialize with the ideal distribution
    probabilities = IdealSoliton(K)
    # Define R
    R = c*(math.log(K/delta)**2)*math.sqrt(K)
    # calculate the additional probabilities
    pivot = int(math.floor(K/R))
    robust_probabilities = [0] + [R/(i*K) for i in range(1, pivot)]
    robust_probabilities += [(R*math.log(R/delta))/K]
    robust_probabilities += [0 for i in range(pivot,K)]
    # add together
    probabilities = np.add(robust_probabilities, probabilities)
    #normalize 
    probabilities /= sum(probabilities)
    return probabilities

def Binary2Bytearray(binary_string): 
    """ Convert a string of binary to bytearray.
    INPUT:
        binary_string: string of binary, so length multiple of 8
    OUTPUT 
        bytearray: bytearray conversion of the string
    """
    return bytearray(int(binary_string,2).to_bytes((len(binary_string)+7) // 8, byteorder='big'))

def PrepareSeed(seed):
    """ Convert seed into a 4 byte long bytearray for packing into droplet
    INPUT:
        seed: integer seed
    OUTPUT 
        seed_index: seed converted to bytearray 
    """
    seed_array = bytearray(Binary2Bytearray(bin(seed)))
    seed_index = bytearray()
    if len(seed_array) < 4:  
        seed_index = bytearray(4-len(seed_array)) + seed_array
    elif len(seed_array) > 4:
        if seed_array[0] == 0:
            del seed_array[0]
            seed_index = seed_array
        else:
            raise Exception("seed too big")
    else: 
        seed_index = seed_array
    return seed_index

def SampleNumber(dist,prng):
    for index, val in enumerate(dist):
        p = prng.random()
        if p < val:
            return index
    return index

def SampleDist_np(dist,prng,np_prng):
    amount = SampleNumber(dist,prng)
    return np_prng.randint(0,len(dist)-1,amount)

def MakeDropletNP(randomized_segments, segment_seed, prng, nr_droplets_probabilities, reed_solo = 2) -> bytearray:
    """ Create droplet from seed and segments
    INPUT:
        randomized_segments: randomized and segmented data.
        segment_seed: integer seed for the creation of the droplet.
        prng: random.Random() random number generator.
    OUTPUT:
        droplet_rs: droplet encoded using Reed Solomon
    """
    seed_index = PrepareSeed(segment_seed)
    np_prng = np.random.RandomState(segment_seed)
    prng.seed(segment_seed)
    segment_indices = SampleDist_np(nr_droplets_probabilities, prng, np_prng)
    segments = [randomized_segments[i] for i in segment_indices]
    droplet = seed_index + bytearray(functools.reduce(lambda i, j: bytes(a^b for (a, b) in zip(i,j)), segments))
    # prepare reedsolomon
    rsc = reedsolo.RSCodec(reed_solo)
    # create the encoded droplet (what will eventually be stored in DNA)
    droplet_rs = rsc.encode(droplet)
    return droplet_rs

def MakeDroplet(randomized_segments, segment_seed, prng, nr_droplets_probabilities, reed_solo = 2) -> bytearray:
    """ Create droplet from seed and segments
    INPUT:
        randomized_segments: randomized and segmented data.
        segment_seed: integer seed for the creation of the droplet.
        prng: random.Random() random number generator.
    OUTPUT:
        droplet_rs: droplet encoded using Reed Solomon
    """
    prng.seed(segment_seed)
    seed_index = PrepareSeed(segment_seed)
    amount = prng.choices(range(0,len(nr_droplets_probabilities)), nr_droplets_probabilities, k = 1)[0]
    segment_indices = prng.sample(range(len(randomized_segments)),k = amount)
    segments = [randomized_segments[i] for i in segment_indices]
    droplet = seed_index + bytearray(functools.reduce(lambda i, j: bytes(a^b for (a, b) in zip(i,j)), segments))
    # prepare reedsolomon
    rsc = reedsolo.RSCodec(reed_solo)
    # create the encoded droplet (what will eventually be stored in DNA)
    droplet_rs = rsc.encode(droplet)
    return droplet_rs

def LFSR():
    """Linear forward shifting register based on Galois fields
    The result is an integer between 0 and 32^2-1 which will not repeat until all possible values have been passed
    """
    mask=0b100000000000000000000000011000101 # Do not change this one
    result = 0b00011011000110110001101100011011 #0b101011100 # Set the first state of the register
    nbits = mask.bit_length()-1
    while True:
        result = (result << 1) #Shift the register left once
        xor = result >> nbits #Shift the register right by the amount of bits in the mask -1
        if xor != 0: #XOR is useless if it is 0
            result ^= mask #XOR the state of the register with the mask

        yield result

def Bytearray2Binary(Bytearray) -> str:
    """ Convert bytearray to binary (string)
    INPUT:
        Bytearray: bytearray to be converted
    OUTPUT:
        binary_string: string of converted bytearray
    """
    binary_string = ""
    for i in Bytearray:
        binary_string += format(i, '08b')
    return binary_string

def Binary2DNA(binary_string):
    """ Convert binary (string) to DNA strand (string)
    Input:
        binary_string: binary strand
    Output:
        dna_string: DNA counterpart
    """
    dna_string = ""
    for x in [binary_string[i:i+2] for i in range(0,len(binary_string),2)]:
        if x == "00":
            dna_string += "A"
        if x == "01":
            dna_string += "C"
        if x == "10":
            dna_string += "G"
        if x == "11":
            dna_string += "T"
    return dna_string

def DNA2Binary(dna_string):
    """ Convert DNA strand (string) to binary (string)
    Input:
        dna_string: DNA strand
    Output:
        binary_string: binary counterpart of s
    """
    binary_string = ""
    for x in dna_string:
        if x == "A":
            binary_string += "00"
        if x == "C":
            binary_string += "01"
        if x == "G":
            binary_string += "10"
        if x == "T":
            binary_string += "11"
    return binary_string

def CheckBiochemicalRequirements(s, max_length=3, check=False):
    """ Check if DNA strand has expected structure
    Input:
        s: DNA strand (string) of A,G,C,T
        length: expected length, normally set at 152
    Output:
        check: Boolean, True or False
    """
    if s.find((max_length+1)*'C') ==-1 & s.find((max_length+1)*'G') ==-1 & s.find((max_length+1)*'T')==-1 & s.find((max_length+1)*'A')==-1:
        nr_CG = s.count('C')+s.count('G')
        per_CG=nr_CG/len(s)
        if (per_CG < 0.55) & (per_CG > 0.45):
            check = True
    return check

def CheckOligoLength(s, length=152, check=False):
    """ Check if DNA strand has expected length
    Input:
        s: a DNA strand (string) of A,G,C,T
        length: expected length, normally set at 152
    Output:
        check: Boolean, True or False
    """
    if len(s) == length:
        check = True
    #else:
    #    if len(s) < length:
    #        print('oligo length is too short')
    #    else:
    #        print('oligo length is too long')
    return check


def RecoverSeed(droplet_seed, total_segments):
    """ Determine segments XORd into this droplet
    INPUT: 
        droplet_seed: seed (integer) of this droplet
        total_segments: total number of segments in input file.
    OUTPUT: 
        amount_recovery: amount of segments in the droplet
        segment_indices: indices of the segments in the droplet
    """
    prng = random.Random()
    prng.seed(droplet_seed)
    amount_recovery = prng.choices(range(0,total_segments+1), RobustSoliton(total_segments,0.001,0.025), k = 1)[0]
    segment_indices = prng.sample(range(total_segments), k = amount_recovery)
    return (amount_recovery, segment_indices)

def SampleDist_np_recover(dist,prng,np_prng):
    amount = SampleNumber(dist,prng)
    return (amount, np_prng.randint(0,len(dist)-1,amount))

def RecoverSeed_np(droplet_seed, total_segments):
    np_prng = np.random.RandomState(droplet_seed)
    prng = random.Random()
    prng.seed(droplet_seed)
    return SampleDist_np_recover(RobustSoliton(total_segments,0.001,0.025), prng, np_prng)

def Decode(input_data, output_data):
    """ Decode the payloads which have one segment not in output_data
    Input:
        inputdata: a list of tuples ([list of segment_indices], payload)
    Output:
        output_data: a dictionary with {nr of segment : value of segment}
    """
    remaining_droplets = []
    newsolves = 0
    for droplet in input_data:
        segment_indices = droplet[0]
        XOR = droplet[1]
        remaining_segments = []
        for i in range(len(segment_indices)):
            if segment_indices[i] in output_data:
                dif = int(XOR,2) ^ int(output_data[segment_indices[i]],2)
                XOR = '{0:0{1}b}'.format(dif,len(droplet[1]))
            else:
                remaining_segments.append(segment_indices[i])    

        if len(remaining_segments)==1:
            output_data[remaining_segments[0]] = XOR
            newsolves=1
        else:
            remaining_droplets.append((remaining_segments, XOR))
    return remaining_droplets, output_data, newsolves

def RemovePadding(solution):
    """ Remove added padding
    Input:
        solution: Binary string of all solved droplets combined
    Output:
        solution: Binary string of solution without paddding
    """
    bits_padded = int(solution[-8:],2)+1
    solution = solution[:-bits_padded]
    return solution