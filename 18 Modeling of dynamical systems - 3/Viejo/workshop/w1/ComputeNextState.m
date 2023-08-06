function [xk, yk]=ComputeNextState(a, p,q, s,x0,y0)
    xk = a + x0 - (x0*(p+q)) + (s*y0);
    yk = (p*x0) - (s*y0) +y0;
end
