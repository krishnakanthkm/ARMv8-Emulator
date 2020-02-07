#EE275 ArmV8 Emulator
#Fall 2018
#
#Samson Kuang
#Krishna Kanth
#Ramji Ghatala
#Tushar Tarihalkar
#
#
#To select which test script to operate on, edit lines 81 to 84
#Comment line 688 to show operands and results for each operation

import sys  #so I can use sys.exit function when reading non-supported command

#Declare 32 Genral Purpose Registers
#   Register #, Register Value, Register Name, Register Description
regs =  [
        [0,0,"X0","arguments/results"],
        [1,0,"X1","arguments/results"],
        [2,0,"X2","arguments/results"],
        [3,0,"X3","arguments/results"],
        [4,0,"X4","arguments/results"],
        [5,0,"X5","arguments/results"],
        [6,0,"X6","arguments/results"],
        [7,0,"X7","arguments/results"],
        [8,0,"X8","indirect result location"],
        [9,0,"X9","temporaries"],
        [10,0,"X10","temporaries"],
        [11,0,"X11","temporaries"],
        [12,0,"X12","temporaries"],
        [13,0,"X13","temporaries"],
        [14,0,"X14","temporaries"],
        [15,0,"X15","temporaries"],
        [16,0,"X16","scratch/temporaries"],
        [17,0,"X17","scratch/temporaries"],
        [18,0,"X18","platform/temporaries"],
        [19,0,"X19","saved"],
        [20,0,"X20","saved"],
        [21,0,"X21","saved"],
        [22,0,"X22","saved"],
        [23,0,"X23","saved"],
        [24,0,"X24","saved"],
        [25,0,"X25","saved"],
        [26,0,"X26","saved"],
        [27,0,"X27","saved"],
        [28,0,"X28","stack pointer"],
        [29,0,"X29","frame pointer"],
        [30,0,"X30","link/return address"],
        [31,0,"XZR","constant 0"]
        ]

#-------Some Global Variables------------        
data_mem = {}   #data memory is a dictionary
label_loc = {}  #store location of labels
pc = 0          #program counter
rm = 0          #source operand value
rn = 0          #source operand value
rd = 0          #destination value
rm_reg = 0      #register for Rm
rn_reg = 0      #register for Rn
rd_reg = 0      #register for Rd
pc_base = 0     #base address of instructions
mem_base = 0    #base address of data
codelines = []  #Declare a reg of code lines  
inst_mem = []
inst_line = []
Nflag = 0
Zflag = 0
Vflag = 0
Cflag = 0



#-------Define Functions---------- 

#Read instruction file, parse, and store into instr_mem
def read_inst():
    global pc_base
    global mem_base
    global inst_mem
    is_instr = True                                     #flag that we are reading instructions
    infile = open("test_fact.txt","r")                  #open file to read
    #infile = open("test_fib.txt","r")                   #open file to read
    #infile = open("test_pow.txt","r")                   #open file to read
    lines = infile.readlines()                          #read all lines of the file and put into "lines"  
    
    for line in lines:
        if ".code" in line:                             #store program counter base offset in pc_base
            pc_base = int(line[6:-2],16)                #get base address for instructions
            #print line
            print "code base addr is: "+str(pc_base)+" hex: "+str("{:08X}".format(pc_base))+ "\n"
        elif ".data" in line:
            mem_base = int(line[6:-1],16)               #get base address for data
            regs[28][1] = mem_base
            regs[29][1] = mem_base
            #print line
            print "memory base addr is: "+str(mem_base)+" hex: "+str("{:08X}".format(mem_base))+"\n"
            is_instr = False
        elif line[0] != "#":
            if is_instr:
                if ":" in line:
                    label_loc[line.split(":")[0]] = len(codelines)  #if line has ":", split it, take 1st element, and store line number
                    codelines.append(line.split(":")[1])            #take second element and store in codelines
                else:
                    codelines.append(line)
            else:
                data_mem[mem_base] = int(line,16)   #store elements of data as hex
                mem_base = mem_base + 1    

    for line in codelines:
        words = line.replace(",","").split()        #delimit by space or comma    
        inst_mem.append(words)
    infile.close()

#Print all of codelines
def print_codelines():
    print "------------------------"
    print "This is in codelines:\n"
    for pc in range(len(codelines)):
        print str(codelines[pc])
    print "\n\n"

#Print all of data memory
def print_data_mem_hex():
    print "------------------------"
    print "This is in data memory (hex):\n"
    print "Address\t\tValue"
    for k,v in data_mem.iteritems():
        print "0x"+"{:08x}".format(k)+"\t0x"+"{:08x}".format(v)
    print "\n\n"
    
#Print all of data memory
def print_data_mem():
    print "------------------------"
    print "This is in data memory (decimal):\n"
    print "Address\t\tValue"
    for k,v in data_mem.iteritems():
        print str(k)+"\t\t"+str(v)
    print "\n\n"

#Print all labels with line number
def print_label_loc():
    print "------------------------"       
    print "This is in labels memory:\n"
    print "Label line"
    for k,v in label_loc.iteritems():
        print k,v
    print "\n\n"
    
#Print all of registers
def print_regs_hex():
    print "------------------------"
    print "This is in registers (hex)\n"
    print "Register\tValue\t\tRegister Function"
    for i in range(len(regs)):
        print str(regs[i][2]) + "\t\t0x"+str("{:08x}".format(regs[i][1])) + "\t" + str(regs[i][3])
    print "\n\n"
    
#Print all of registers
def print_regs():
    print "------------------------"
    print "This is in registers (dec)\n"
    print "Register\tValue\t\tRegister Function"
    for i in range(len(regs)):
        print str(regs[i][2]) + "\t\t"+str((regs[i][1])) + "\t\t" + str(regs[i][3])
    print "\n\n"
    
#Print all of instruction memory
def print_inst_mem():
    print "------------------------"
    print "This is in instruction memory:\n"
    for pc in range(len(inst_mem)):
        print str(inst_mem[pc])
    print "Number of instructions is: "+str(len(inst_mem))+"\n"
    print "\n\n"

#Print Rd, Rm, Rn for R-Format Instructions (ADD, ADDI, SUB, SUBI, MUL, using XZR and constant #<number>)
def print_reg_r_format(pc, rm, rn, rd, rm_reg, rn_reg, rd_reg):
    print "rm contains X" +str(rm_reg) +"=" +str(rm) +", binary: " +str("{:08b}".format(rm))    #rm contains X0 = number
    print "rn contains X" +str(rn_reg) +"=" +str(rn) +", binary: " +str("{:08b}".format(rn))    #rn contains X1 = number
    print "rd contains X" +str(rd_reg) +"=" +str(rd) +", binary: " +str("{:08b}".format(rd))    #rd contains X2 = number
    print "Line " +str(pc) +"= of regs: "+str(regs[int(rd_reg)])+"\n"                           #print the whole register line at destination

def print_flags():
    print "N = " + str(Nflag)
    print "Z = " + str(Zflag)
    print "C = " + str(Cflag)
    print "V = " + str(Vflag)
    print "\n"
    
#Allocate Rd, Rm, Rn for R-Format instructions
def get_r_format_operands(pc):

    #get location of Rd
    if inst_mem[pc][1] == "XZR":        #if XZR, then look at register 31
        rd_reg = "31"
    elif inst_mem[pc][1] == "SP":       #if SP, then look at register 28
        rd_reg = "28"   
    else:
        rd_reg = inst_mem[pc][1][1:]    #[1:] strip "X" from "X0". rd = register 0, destination

    #if 3rd operand has ], like SUBI SP [SP #16]...
    if "]" in inst_mem[pc][3]:
    
        #get location and value for Rm
        if "XZR" in inst_mem[pc][2]:        #if XZR, then look at register 31
            rm_reg = "31"
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
        elif "SP" in inst_mem[pc][2]:       #if SP, then look at register 28
            rm_reg = "28"
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
        elif "#" in inst_mem[pc][2]:        #if constant, then strip "#" and make rm constant number
            rm_reg = "Constant"
            rm = int(inst_mem[pc][2][2:])   #[1:] strips the "[#" character
        else:                               #if register X10 then look at register X10
            rm_reg = inst_mem[pc][2][2:]    #[2:] strips the "[X" character
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
    
        #get location and value for Rn
        if "XZR" in inst_mem[pc][3]:        #if XZR, then look at register 31
            rn_reg = "31"
            rn = regs[int(rn_reg)][1]       #rn is assigned the value stored in register
        elif "SP" in inst_mem[pc][3]:       #if SP, then look at register 28
            rn_reg = "28"
            rn = regs[int(rn_reg)][1]       #rn is assigned the value stored in register
        elif "#" in inst_mem[pc][3]:        #if constant, then strip "#" and make rn constant number
            rn_reg = "Constant"
            rn = int(inst_mem[pc][3][1:-1]) #[1:-1] strips the "#" and "]" character
            rn = rn / 8                     #takes #16 and divides by 8bytes/register, to give offset of 2
        else:                               #if register X10 then look at register X10
            rn_reg = inst_mem[pc][3][1:-1]  #[1:-1] strips the "X" and "]" character
            rn = regs[int(rn_reg)][1]       #rm is assigned the value stored in register
            rn = rn / 8                     #takes #16 and divides by 8bytes/register, to give offset of 2 
    
    else:

        #get location and value for Rm
        if inst_mem[pc][2] == "XZR":        #if XZR, then look at register 31
            rm_reg = "31"
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
        elif inst_mem[pc][2] == "SP":       #if SP, then look at register 28
            rm_reg = "28"
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
        elif "#" in inst_mem[pc][2]:        #if constant, then strip "#" and make rm constant number
            rm_reg = "Constant"
            rm = int(inst_mem[pc][2][1:])   #[1:] strips the "#" character
        else:                               #if register X10 then look at register X10
            rm_reg = inst_mem[pc][2][1:]    #[1:] strips the "X" character
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
        
        #get location and value for Rn
        if inst_mem[pc][3] == "XZR":        #if XZR, then look at register 31
            rn_reg = "31"
            rn = regs[int(rn_reg)][1]       #rn is assigned the value stored in register
        elif inst_mem[pc][3] == "SP":       #if SP, then look at register 28
            rn_reg = "28"
            rn = regs[int(rn_reg)][1]       #rn is assigned the value stored in register
        elif "#" in inst_mem[pc][3]:        #if constant, then strip "#" and make rn constant number
            if inst_mem[pc][2] == "SP":
                rn_reg = "Constant"
                rn = int(inst_mem[pc][3][1:]) / 8
            else:
                rn_reg = "Constant"
                rn = int(inst_mem[pc][3][1:])   #[1:] strips the "#" character
        elif inst_mem[pc][2] == "SP":
                rn_reg = inst_mem[pc][3][1:]
                print rn_reg
                rn = regs[int(rn_reg)][1] / 8

        else:                               #if register X10 then look at register X10
            rn_reg = inst_mem[pc][3][1:]    #[1:] strips the "X" character
            rn = regs[int(rn_reg)][1]       #rm is assigned the value stored in register
    return (rm, rn, rd, rm_reg, rn_reg, rd_reg)

#Get operands for LOAD instructions
#LDR X1 [X3 X5]
#LDR X1 [X3 #8]
#LDR X1 [X3]
#LDR SP [SP #8]
#    Rd  Rm  Rn
def get_load_operands(pc):

    #get location of Rd
    if inst_mem[pc][1] == "XZR":        #if XZR, then look at register 31
        rd_reg = "31"
    elif inst_mem[pc][1] == "SP":       #if SP, then look at register 28
        rd_reg = "28"
    else:
        rd_reg = inst_mem[pc][1][1:]    #[1:] strip "X" from "X0". rd = register 0, destination

    #if LOAD instruction is type: LDR X1 [X3], get Rm
    #if LOAD instruction is type: LDR SP [X3], get Rm
    if "]" in inst_mem[pc][2]:
        #get location and value for Rm
        if "XZR" in inst_mem[pc][2]:        #if XZR, then look at register 31
            rm_reg = "31"
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
        elif "SP" in inst_mem[pc][2]:       #if SP, then look at register 28
            rm_reg = "28"
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
        elif "#" in inst_mem[pc][2]:        #if constant, then strip "#" and make rm constant number
            rm_reg = "Constant"
            rm = int(inst_mem[pc][2][1:])   #[1:] strips the "#" character
        else:                               #if register X10 then look at register X10
            rm_reg = inst_mem[pc][2][2:-1]  #[2:-1] strips the "[X" and "]" characters
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in mem register
            
        rn_reg=0
        rn=0
        
    #if LOAD instruction is type: LDR X1 [X3 #8], get Rm and Rn
    #if LOAD instruction is type: LDR X1 [X3 X5], get Rm and Rn
    elif "]" in inst_mem[pc][3]:
        #get location and value for Rm
        if "XZR" in inst_mem[pc][2]:        #if XZR, then look at register 31
            rm_reg = "31"
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
        elif "SP" in inst_mem[pc][2]:       #if SP, then look at register 28
            rm_reg = "28"
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
        elif "#" in inst_mem[pc][2]:        #if constant, then strip "#" and make rm constant number
            rm_reg = "Constant"
            rm = int(inst_mem[pc][2][2:])   #[1:] strips the "[#" character
        else:                               #if register X10 then look at register X10
            rm_reg = inst_mem[pc][2][2:]    #[2:] strips the "[X" character
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
    
        #get location and value for Rn
        if "XZR" in inst_mem[pc][3]:        #if XZR, then look at register 31
            rn_reg = "31"
            rn = regs[int(rn_reg)][1]       #rn is assigned the value stored in register
        elif "SP" in inst_mem[pc][3]:       #if SP, then look at register 28
            rn_reg = "28"
            rn = regs[int(rn_reg)][1]       #rn is assigned the value stored in register
        elif "#" in inst_mem[pc][3]:        #if constant, then strip "#" and make rn constant number
            rn_reg = "Constant"
            rn = int(inst_mem[pc][3][1:-1]) #[1:-1] strips the "#" and "]" character
            rn = rn / 8                     #takes #16 and divides by 8bytes/register, to give offset of 2
        else:                               #if register X10 then look at register X10
            rn_reg = inst_mem[pc][3][1:-1]  #[1:-1] strips the "X" and "]" character
            rn = regs[int(rn_reg)][1]       #rm is assigned the value stored in register
            rn = rn / 8                     #takes #16 and divides by 8bytes/register, to give offset of 2
            
    return (rm, rn, rd, rm_reg, rn_reg, rd_reg)

#Get operands for STORE instructions
#STR X1 [X3 X5]
#STR X1 [X3 #8]
#STR X1 [X3]
#    Rd  Rm  Rn
def get_store_operands(pc):

    #get location of Rd
    if inst_mem[pc][1] == "XZR":        #if XZR, then look at register 31
        rd_reg = "31"
    elif inst_mem[pc][1] == "SP":       #if SP, then look at register 28
        rd_reg = "28"
    else:
        rd_reg = inst_mem[pc][1][1:]    #[1:] strip "X" from "X0". rd = register 0, destination

    #if STORE instruction is type: STR X1 [X3], get Rm
    if "]" in inst_mem[pc][2]:
        #get location and value for Rm
        if "XZR" in inst_mem[pc][2]:        #if XZR, then look at register 31
            rm_reg = "31"
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
        elif "SP" in inst_mem[pc][2]:       #if SP, then look at register 28
            rm_reg = "28"
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
        elif "#" in inst_mem[pc][2]:        #if constant, then strip "#" and make rm constant number
            rm_reg = "Constant"
            rm = int(inst_mem[pc][2][1:])   #[1:] strips the "#" character
        else:                               #if register X10 then look at register X10
            rm_reg = inst_mem[pc][2][2:-1]  #[2:-1] strips the "[X" and "]" characters
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in mem register
            
        rn_reg=0
        rn=0
        
    #if STORE instruction is type: STR X1 [X3 #8], get Rm and Rn
    #if STORE instruction is type: STR X1 [X3 X5], get Rm and Rn
    elif "]" in inst_mem[pc][3]:
        #get location and value for Rm
        if "XZR" in inst_mem[pc][2]:        #if XZR, then look at register 31
            rm_reg = "31"
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
        if "SP" in inst_mem[pc][2]:         #if SP, then look at register 28
            rm_reg = "28"
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
        elif "#" in inst_mem[pc][2]:        #if constant, then strip "#" and make rm constant number
            rm_reg = "Constant"
            rm = int(inst_mem[pc][2][2:])   #[2:] strips the "[#" character
        else:                               #if register X10 then look at register X10
            rm_reg = inst_mem[pc][2][2:]    #[2:] strips the "[X" character
            rm = regs[int(rm_reg)][1]       #rm is assigned the value stored in register
    
        #get location and value for Rn
        if "XZR" in inst_mem[pc][3]:        #if XZR, then look at register 31
            rn_reg = "31"
            rn = regs[int(rn_reg)][1]       #rn is assigned the value stored in register
        if "SP" in inst_mem[pc][3]:         #if SP, then look at register 28
            rn_reg = "28"
            rn = regs[int(rn_reg)][1]       #rn is assigned the value stored in register
        elif "#" in inst_mem[pc][3]:        #if constant, then strip "#" and make rn constant number
            rn_reg = "Constant"
            rn = int(inst_mem[pc][3][1:-1]) #[1:-1] strips the "#" and "]" character
            rn = rn / 8                     #takes #16 and divides by 4bytes/register, to give offset of 2
        else:                               #if register X10 then look at register X10
            rn_reg = inst_mem[pc][3][1:-1]  #[1:-1] strips the "X" and "]" character
            rn = regs[int(rn_reg)][1]       #rm is assigned the value stored in register
            rn = rn / 8                     #takes #16 and divides by 4bytes/register, to give offset of 2
            
    return (rm, rn, rd, rm_reg, rn_reg, rd_reg)

#Get operands for COMPARE instructions
#CBNZ X1 #25
#CBZ X1 L2
#    Rd  Rm  Rn
def get_compare_operands(pc):

    #get location of Rd
    if inst_mem[pc][1] == "XZR":        #if XZR, then look at register 31
        rd_reg = "31"
    else:
        rd_reg = inst_mem[pc][1][1:]    #[1:] strip "X" from "X0". rd = register 0, destination
        
    #get location and value for Rm
    if "#" in inst_mem[pc][2]:          #if constant, then strip "#" and make rm constant number
        rm_reg = "Constant"
        rm = int(inst_mem[pc][2][1:])   #[1:] strips the "#" character
    else:                               #if L2, then store value L2 in Rm
        rm_reg = "Loop"     
        rm = label_loc[inst_mem[pc][2]]   

    rn_reg= 0
    rn=0
            
    return (rm, rn, rd, rm_reg, rn_reg, rd_reg)
    
#Get operands for BRANCH instructions
#BR X30
#BR L1
#    Rm  Rn    Rd not used
def get_branch_operands(pc):

    #get location of Rd
    if inst_mem[pc][1] == "XZR":        #if XZR, then look at register 31
        rm_reg = "31"
        rm = regs[int(rm_reg)][1]
    elif "X" in inst_mem[pc][1]:
        rm_reg = inst_mem[pc][1][1:]    #[1:] strip "X" from "X0". rd = register 0, destination
        rm = regs[int(rm_reg)][1]
    else:                               #if L2, then store value L2 in Rm
        rm_reg = 0     
        rm = label_loc[inst_mem[pc][1]]   
    
    rd_reg= 0
    
    rn_reg= 0
    rn=0
            
    return (rm, rn, rd, rm_reg, rn_reg, rd_reg)
    
def twos_complement(val, nbits):
    """Compute the 2's complement of int value val"""
    if val < 0:
        val = (1 << nbits) + val
    else:
        if (val & (1 << (nbits - 1))) != 0:
            # If sign bit is set.
            # compute negative value.
            val = val - (1 << nbits)
    return val

def check_overflow_flag(rm,rn):
    if(rm < 0):
        temp = twos_complement(rm,64)
        rm = temp
    if(rn < 0):
        temp1 = twos_complement(rn,64)
        rn = temp1
    sum = rm+rn
    if((rm>>63)==0 and (rn>>63)==0 and (sum>>63)==1):
        return 1
    elif((rm>>63)==1 and (rn>>63)==1 and (sum>>63)==(0 or 2)):       #2 is required in case there is a carry to the 65th bit
        return 1
    else:
        return 0
    
def check_carry_flag_add(rm,rn):
    if(rm<0):
        temp = twos_complement(rm,64)
        rm = temp
    if(rn<0):
        temp_1 = twos_complement(rn,64)
        rn = temp_1
    sum = rm + rn
    if((sum>>64)==1):
        return 1;
    else:
        return 0;

def check_carry_flag_sub(rm,rn):
    if(rm<0):
        temp = twos_complement(rm,64)
        rm = temp
    if(rn<0):
        temp_1 = twos_complement(rn,64)
        rn = temp_1
    if(rm<rn):                                  #The carry flag is set if the subtraction of two numbers requires a borrow
        return 1
        
#-------Start Main---------- 
def main():
    print "\nThis is main\n"
    read_inst()      #Read instruction file, parse, and store into instr_mem
    #print_codelines()
    #print_data_mem()
    #print_label_loc()
    print_inst_mem()
    
    print "------------------------"
    print "Start Operations:\n"
    global pc
    global Zflag
    global Nflag
    global Vflag
    global Cflag
    while pc < len(inst_mem):
        print "Line " +str(pc) +" is an " +str(inst_mem[pc][0])+ " instruction. "+str(inst_mem[pc])
        
        #-----------Do R-FORMAT calculations with Rm Rn and store to Rd----------------
        
        if   inst_mem[pc][0] == "ADD"   or inst_mem[pc][0] == "ADDI":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_r_format_operands(pc)    #get Rd, Rm, and Rn
            regs[int(rd_reg)][1] = rm + rn          #perform ADD and place into register memory
            pc = pc+1
            
        if   inst_mem[pc][0] == "ADDS"   or inst_mem[pc][0] == "ADDIS":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_r_format_operands(pc)    #get Rd, Rm, and Rn
            regs[int(rd_reg)][1] = rm + rn          #perform ADD and place into register memory
            
            if regs[int(rd_reg)][1] >= 0:
                Nflag = 0
            else:
                Nflag = 1
            if regs[int(rd_reg)][1] == 0:
                Zflag = 1
            else:
                Zflag = 0
            
            Vflag = check_overflow_flag(rm,rn)
            Cflag = check_carry_flag_add(rm,rn) 
            
            print_flags()
            pc = pc+1
            
        elif inst_mem[pc][0] == "SUB"   or inst_mem[pc][0] == "SUBI":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_r_format_operands(pc)    #get Rd, Rm, and Rn
            regs[int(rd_reg)][1] = rm - rn          #perform SUB and place into registor memory
            pc = pc+1
        
        elif inst_mem[pc][0] == "SUBS"   or inst_mem[pc][0] == "SUBIS":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_r_format_operands(pc)    #get Rd, Rm, and Rn
            regs[int(rd_reg)][1] = rm - rn          #perform SUB and place into registor memory
            
            if regs[int(rd_reg)][1] >= 0:
                Nflag = 0
            else:
                Nflag = 1
            if regs[int(rd_reg)][1] == 0:
                Zflag = 1
            else:
                Zflag = 0
            
            Vflag = check_overflow_flag(rm,rn)
            Cflag = check_carry_flag_sub(rm,rn) 
            
            print_flags()    
            pc = pc+1
            
        elif inst_mem[pc][0] == "MUL":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_r_format_operands(pc)    #get Rd, Rm, and Rn
            regs[int(rd_reg)][1] = rm * rn          #perform MUL and place into register memory
            pc = pc+1
            
        #-----------Do LOGICAL calculations with Rm Rn and store to Rd----------------
        
        elif inst_mem[pc][0] == "AND"   or inst_mem[pc][0] == "ANDI":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_r_format_operands(pc)    #get Rd, Rm, and Rn
            regs[int(rd_reg)][1] = rm & rn          #perform AND and place into register memory
            pc = pc+1
            
        elif inst_mem[pc][0] == "ORR"   or inst_mem[pc][0] == "ORRI":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_r_format_operands(pc)    #get Rd, Rm, and Rn
            regs[int(rd_reg)][1] = rm | rn          #perform OR and place into registor memory
            pc = pc+1
            
        elif inst_mem[pc][0] == "EOR"   or inst_mem[pc][0] == "EORI":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_r_format_operands(pc)    #get Rd, Rm, and Rn
            regs[int(rd_reg)][1] = rm ^ rn          #perform XOR and place into register memory
            pc = pc+1
            
        elif inst_mem[pc][0] == "LSL":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_r_format_operands(pc)    #get Rd, Rm, and Rn
            regs[int(rd_reg)][1] = rm << rn         #perform LSL and place into register memory
            pc = pc+1
            
        elif inst_mem[pc][0] == "LSR":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_r_format_operands(pc)    #get Rd, Rm, and Rn
            regs[int(rd_reg)][1] = rm >> rn         #perform LSR and place into register memory
            pc = pc+1
        
        #-----------Do LOAD/STORE operations----------------
        elif inst_mem[pc][0] == "LDR" or inst_mem[pc][0] == "LDUR":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_load_operands(pc)
            regs[int(rd_reg)][1] = data_mem[rm + rn]
            pc = pc+1
            #print_data_mem()
            
        elif inst_mem[pc][0] == "STR" or inst_mem[pc][0] == "STUR":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_store_operands(pc)
            data_mem[rm+rn] = regs[int(rd_reg)][1]
            pc = pc+1
            #print_data_mem()
            
        #-----------Do COMPARE operations----------------
        elif inst_mem[pc][0] == "CBNZ":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_compare_operands(pc)    #get Rd, Rm, and Rn
            
            if regs[int(rd_reg)][1] != 0:
                if "#" in regs[int(rd_reg)][2]:
                    pc = pc + (rm * 4)                  #for CBNZ X1 #25, pc goes to pc + 100
                else:
                    pc = rm                             #for CBNZ X1 X30
            else:
                print "we have 0!!!!"
                pc = pc+1
        elif inst_mem[pc][0] == "CBZ":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_compare_operands(pc)    #get Rd, Rm, and Rn
            
            if regs[int(rd_reg)][1] == 0:
                if "#" in regs[int(rd_reg)][2]:
                    pc = pc + (rm * 4)                  #for CBZ X1 #25, pc goes to pc + 100
                else:
                    pc = rm                             #for CBZ X1 X30
                print "we have 0!!!!"
            else:
                pc = pc+1

        #-----------Do BRANCH operations----------------
        elif inst_mem[pc][0] == "BR":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_branch_operands(pc)    #get Rd, Rm, and Rn
            #if rm = frame pointer
            if rm == regs[29][1]:
                break
            else:
                pc = rm
                
        elif inst_mem[pc][0] == "B":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_branch_operands(pc)    #get Rd, Rm, and Rn
            pc = rm

        elif inst_mem[pc][0] == "BL":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_branch_operands(pc)    #get Rd, Rm, and Rn
            regs[30][1] = pc+1      #X30 stores the next instruction, but PC branches
            pc = rm
            
        elif inst_mem[pc][0] == "B.GE":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_branch_operands(pc)    #get Rd, Rm, and Rn
            print_flags()
            if Nflag == Vflag:
                pc = rm
            else:
                pc = pc+1

        elif inst_mem[pc][0] == "B.GT":
            (rm, rn, rd, rm_reg, rn_reg, rd_reg) = get_branch_operands(pc)    #get Rd, Rm, and Rn
            print_flags()
            if Nflag == Vflag & Zflag ==0:
                pc = rm
            else:
                pc = pc+1

        #----------End of Operations-----------------------------------------
        #----------Assign value to Rd and print registers---------------------
        rd = regs[int(rd_reg)][1]       #assign value rd_reg to rd for printing
        print_reg_r_format(pc, rm, rn, rd, rm_reg, rn_reg, rd_reg)
    
        #OVERWRITE register 31 after each operation, always 0
        regs[31][1] = 0        
        
    

    #----------Print output for presentation---------------------
    print_regs()
    print_regs_hex()
    print_data_mem()
    print_data_mem_hex()
    print_flags()
    print "END OF PROGRAM."
        
if __name__== "__main__":
    main()
