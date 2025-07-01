#pragma once

#include <iostream>
#include <iomanip>
#include <conio.h>
#include <queue>
#include <string>
#include <algorithm>
#include <vector>

using namespace std;

#define MaxBlocks 4		
#define EMPTY_BLOCK -1		
#define OTAL_INSTRUCTIONS 320	
typedef int InstNumber;	
typedef int PageNumber;
typedef int BlockNumber;	

class Memory
{
private:
	vector<PageNumber> memoryBlocks;//内存块
	vector<bool> instructionExecuted;//是否执行过该指令
	queue<BlockNumber> LRU_Queue;	//最近最少使用队列

	int executionCount = 0;				            //运行次数
	int pageFaultCount = 0;					       //缺页次数
	int remainingInstructions = OTAL_INSTRUCTIONS;//剩余未执行指令

	void execute(string algorithm, InstNumber aim);			     //执行一条指令
	PageNumber adjust(string algorithm, BlockNumber& pos);		//页面置换

public:
	Memory() = default;
	~Memory() = default;

	void Init();		
	void Simulate(string algorithm);			

	int getRunTime() { return this->executionCount; }			
	int getmissPageTime() { return this->pageFaultCount; }	
	double getmissPageRate() { return (1.0 * this->pageFaultCount / this->executionCount); }	
}; 
