function [x,y]=InitializeVariablesRandomly(x,y)
    %Acceptable intervals for x (initial ammout of lead in plasma).
    randmin = 0;
    randmax = 0.05;
    r = (randmax-randmin).*rand + randmin;
    x = r;

    %because the acceptable amount of lead in plasma is bewteen 0 and 1 mg, 
    %and rand generates a number between 0 and 1,  there is no need 
    %to add thersholds to y.
    y = rand;
end
