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
	vector<PageNumber> memoryBlocks;//�ڴ��
	vector<bool> instructionExecuted;//�Ƿ�ִ�й���ָ��
	queue<BlockNumber> LRU_Queue;	//�������ʹ�ö���

	int executionCount = 0;				            //���д���
	int pageFaultCount = 0;					       //ȱҳ����
	int remainingInstructions = OTAL_INSTRUCTIONS;//ʣ��δִ��ָ��

	void execute(string algorithm, InstNumber aim);			     //ִ��һ��ָ��
	PageNumber adjust(string algorithm, BlockNumber& pos);		//ҳ���û�

public:
	Memory() = default;
	~Memory() = default;

	void Init();		
	void Simulate(string algorithm);			

	int getRunTime() { return this->executionCount; }			
	int getmissPageTime() { return this->pageFaultCount; }	
	double getmissPageRate() { return (1.0 * this->pageFaultCount / this->executionCount); }	
}; 
