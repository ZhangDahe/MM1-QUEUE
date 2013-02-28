'''
Created on Feb 16, 2013
@author: adrielklein

This module defines an MM1 Queuing System Simulator. Three class are defined in this module: Request, Controller, and Monitor.

The Request object represents a request which enters the system (gets born), waits in a queue, gets served, and leaves (dies).
Each request object has a record of its birth time, time at which it was serviced, and time at which it was born.

The Controller object is what manages the requests. the controller puts new requests into the queue and services each request
once it is at the front of the queue.

The Monitor object keeps records statistics about the queuing system at various points in time. The monitor gets information
about the system when the controller sends it a snapshot of the system.

So there is one instance of a Controller, one instance of a Monitor, and many instances of a request. The controller continually
creates new requests according to an exponential distributed arrival rate and continually serves the requests according to an exponentially
distributed service rate. 

This is a single server queue so there can be at most one request being served at a given time. Incoming requests are served on a first-come
first-serve basis.
'''
from __future__ import division #Required for floating point divison.
from math import sqrt # Required to find variance
from heapq import heappush, heappop
from NumberGenerator import exponentialValue # Required to generate exponentially distributed random numbers

class Controller:
    def __init__(self, arrivalRate, averageServiceTime, simulationTime):
        self.arrivalRate = arrivalRate
        self.serviceRate = 1/averageServiceTime
        self.simulationTime = simulationTime
        self.time = 0
        self.queue = [] # A queue of events waiting to be served
        self.beingServed = None # The request being served. None if no request is being served.
        self.recentlyDied = None
        self.monitor = Monitor() # Collects information about the state of the queue.
        # Schedule is a heap with times as keys and events as values.
        # The events will be representing by the following strings:
        # "Birth", "Death", and "Monitor"
        self.schedule = []
        
    def runSimulation(self, monitorStartingTime):
        self.monitorStartingTime = monitorStartingTime
        #Add first Birth event to schedule
        heappush(self.schedule, (exponentialValue(self.arrivalRate), "Birth"))
        #Add first Monitor event to schedule.
        heappush(self.schedule, (monitorStartingTime, "Monitor"))
        
        while self.time < self.simulationTime:
            '''
            print str(self.time) + ": " + str(self.schedule)
            print "Items in queue: " + str(len(self.queue))
            print "Item in server: " + str(self.beingServed)
            
            if self.sampleRequest != None:
                print "Sample Waiting Time: " + str(self.recentlyDied.getWaitingTime())
                print "Sample Queuing Time: " + str(self.sampleRequest.getQueueingTime())
            '''
            
            #Get the next event from the schedule
            pair = heappop(self.schedule)
            self.time = pair[0]
            event = pair[1]
            self.executeEvent(event)
            
    def executeEvent(self,event):
        if event =="Birth":
            if self.time > self.monitorStartingTime:
                self.monitor.incrementAttemptedRequests()
            if len(self.queue) == 4:
                if self.time > self.monitorStartingTime:
                    self.monitor.incrementRejectedRequests()
                #Schedule next birth and return
                timeOfNextBirth = self.time + exponentialValue(self.arrivalRate)
                heappush(self.schedule, (timeOfNextBirth, "Birth"))
                return
            #Create new request and enqueue
            newRequest = Request(self.time)
            self.queue.append(newRequest)
            #Schedule next birth
            timeOfNextBirth = self.time + exponentialValue(self.arrivalRate)
            heappush(self.schedule, (timeOfNextBirth, "Birth"))
            
            # If queue only has one request and no requests are being served, then
            # dequeue the request, start serving request, and schedule death
            if len(self.queue) == 1 and self.beingServed == None:
                request = self.queue.pop(0)
                request.setServiceTime(self.time)
                self.beingServed = request
                #Schedule a death
                deathTime = self.time + 0.015
                heappush(self.schedule, (deathTime, "Death"))
        elif event == "Death":
            self.recentlyDied = self.beingServed
            self.recentlyDied.setDeathTime(self.time)
            '''
            if self.time > self.monitorStartingTime:
                self.monitor.recordDeadRequest(self.recentlyDied)
            '''
            self.beingServed = None
            # Now there are no requests being served. If queue is empty, do nothing. Otherwise serve next request.
            if len(self.queue) != 0:
                request = self.queue.pop(0)
                request.setServiceTime(self.time)
                self.beingServed = request
                #Schedule a death
                deathTime = self.time + 0.015
                heappush(self.schedule, (deathTime, "Death"))
        else:
            #This must be a monitor event
            requestsWaiting = len(self.queue)
            requestsInSystem = requestsWaiting
            if self.beingServed != None:
                requestsInSystem += 1            
            self.monitor.recordSnapshot(requestsWaiting, requestsInSystem, self.recentlyDied)
            #Schedule next monitor event.
            nextMonitorTime = self.time + exponentialValue(self.arrivalRate/2)
            heappush(self.schedule, (nextMonitorTime, "Monitor"))
            
class Request:
    def __init__(self, birthTime):
        self.birthTime = birthTime
    def setServiceTime(self, serviceTime):
        self.serviceTime = serviceTime
    def setDeathTime(self, deathTime):
        self.deathTime = deathTime
    def getWaitingTime(self):
        return self.serviceTime - self.birthTime
    def getQueuingTime(self):
        return self.deathTime - self.birthTime
    
class Monitor:
    def __init__(self):
        self.numSnapshots = 0
        self.numRequests = 0
        self.attemptedRequests = 0
        self.rejectedRequests = 0
        self.requestsWaiting = []
        self.requestsInSystem = []
        self.waitingTimes = []
        self.queuingTimes = []
    def recordSnapshot(self, requestsWaiting, requestsInSystem, recentlyDied):
        self.numSnapshots += 1
        self.queuingTimes.append(recentlyDied.getQueuingTime())
        self.requestsWaiting.append(requestsWaiting)
        self.requestsInSystem.append(requestsInSystem)
    def getMeanOfRequestsInSystem(self):
        return sum(self.requestsInSystem)/self.numSnapshots
    def getStandardDeviationOfRequestsInSystem(self):
        mean = self.getMeanOfRequestsInSystem()
        squaredDifferences = [(x - mean)**2 for x in self.requestsInSystem]
        variance = sum(squaredDifferences) / self.numSnapshots
        standardDeviation = sqrt(variance)
        return standardDeviation
    
    def incrementAttemptedRequests(self):
        self.attemptedRequests += 1
        
    def incrementRejectedRequests(self):
        self.rejectedRequests += 1
        
    def getRejectionProbability(self):
        return self.rejectedRequests/ self.attemptedRequests
    
    def getStandardDeviationOfRequestResult(self):
        mean = self.getRejectionProbability()
        variance = (self.rejectedRequests*(0 - mean)**2 + (self.attemptedRequests - self.rejectedRequests)*(1 - mean)**2)/self.attemptedRequests
        standardDeviation = sqrt(variance)
        return standardDeviation
    def getStandardDeviationOfQueuingTime(self):
        mean = sum(self.queuingTimes)/self.numSnapshots
        squaredDifferences = [(x - mean)**2 for x in self.queuingTimes]
        variance = sum(squaredDifferences)/ len(self.queuingTimes)
        standardDeviation = sqrt(variance)
        return standardDeviation

    
    def recordDeadRequest(self, request):
        self.numRequests += 1
        self.waitingTimes.append(request.getWaitingTime())
        self.queuingTimes.append(request.getQueuingTime())
    def printReport(self):
        print "Number of Snapshots Taken: " + str(self.numSnapshots)
        print "Average Requests In System: "  + str(sum(self.requestsInSystem)/self.numSnapshots)
        print "Standard Deviation of Requests In System " + str(self.getStandardDeviationOfRequestsInSystem())
        print
        print "Number of Dead Requests: " + str(self.numSnapshots)
        print "Average Queuing Time: " + str(sum(self.queuingTimes)/self.numSnapshots)
        print "Standard Deviation of Queuing Time: " + str(self.getStandardDeviationOfQueuingTime())
        print
        print "Number of Requests Who Tried to Enter " + str(self.attemptedRequests)
        print "Standard Deviation of Requests who were successful: " + str(self.getStandardDeviationOfRequestResult())
        print "Rejection Probability: " + str(self.getRejectionProbability())
        print


myController = Controller(60, 0.45, 200) 
# Begin the simulation and start monitoring system at time 100.
myController.runSimulation(100)
#Print the results of the simulation
myController.monitor.printReport()
print

        