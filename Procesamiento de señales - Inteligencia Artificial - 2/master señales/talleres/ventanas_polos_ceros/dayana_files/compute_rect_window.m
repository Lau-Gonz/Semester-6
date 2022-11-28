function [H] = compute_rect_window (w, poles, zeros)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   
%   INPUT: w -> es el rango de frecuencias
%          poles -> vector con los distintos polos
%          zeros -> vector con los distintos zeros
%   
%   Output: H -> respuesta en frecuencia zeros/polos
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    jw = 1i.*w;

    den = (jw - poles(1) ).*(jw - conj( poles(1) )).*(jw - poles(1) ).*(jw - conj( poles(1) ));
    
    for p = 2:length( poles )
        %numero de polos debe ser de mayor orden que el numerador
        den = (jw - poles(p) ).*(jw - conj( poles(p) )).*(jw - poles(p) ).*(jw - conj( poles(p) )).*den;
    end
   
    
    %solo se pone una vez por que el primer cero está en el origen
    num = (jw - zeros(1)); 
    
    for z = 2:length(zeros)
        
        num = (jw - zeros(z)).*(jw - conj( zeros(z) )).* num;
    end
   
    H = num./den;
    H = H./max(abs(H));
end
    

