function [H] = high_pass_win(w, poles, zeros)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   
%   INPUT: w -> es el rango de frecuencias
%          poles -> escalar 1
%          zeros -> vector con los distintos zeros
%   
%   Output: H -> respuesta en frecuencia zeros/polos
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    jw = 1i.*w;

    den = poles;
    
    %solo se pone una vez por que el primer cero está en el origen
    num = (jw - zeros(1)); 
    
    for z = 2:length(zeros)
        
        num = (jw - zeros(z)).*(jw - conj( zeros(z) )).* num;
    end
   
    H = num./den;
    H = H./max(abs(H));
end