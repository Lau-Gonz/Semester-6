clear all
close all
clc
%set values
a = 0.06;
p = 0.4;
q = 0.2;
s = 0.3;
numberOfDays = 200;
x=a;
y=0;

%random values
[x,y]=InitializeVariablesRandomly(x,y);
x;
y;
figureHandle = figure('Name','Simulation of lead in human body');
hold on;
set(figureHandle, 'Position', [50,50,500,200]);
set(figureHandle, 'DoubleBuffer', 'on');
plotHandleFirstVariable = plot(0:numberOfDays, zeros(1,numberOfDays+1));
plotHandleSecondVariable = plot(0:numberOfDays, zeros(1,numberOfDays+1));
hold off;

drawnow;
for iDay=1:numberOfDays+1
    plotVectorX = get(plotHandleFirstVariable, 'YData');
    plotVectorX (iDay) = x;
    plotVectorY = get(plotHandleSecondVariable, 'YData');
    plotVectorY (iDay) = y;
    set (plotHandleFirstVariable, 'YData',plotVectorX);
    set (plotHandleSecondVariable, 'YData',plotVectorY);
    drawnow;
    [x, y]=ComputeNextState(a, p,q, s,x,y);
    legend([plotVectorX, plotVectorY], ["Lead in plasma", "Lead in bones"]);
end



