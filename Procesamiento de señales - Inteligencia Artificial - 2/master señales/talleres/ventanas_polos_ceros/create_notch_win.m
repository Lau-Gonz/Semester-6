function [H_H_C] = create_notch_win(distance, time, freq, jw, reject_hz, graph_)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   Input:  distance -> parte real de los polos
%           time -> vector del tiempo de la señal
%           freq -> vector de las frecuencias de la señal
%           jw -> vector de frecuencias angulares de la señal
%           reject_hz -> frecuencia que se quiere borrar con el notch
%           graph_ -> graficar o no graficar
%   Output:
%           H_H_C -> respuesta en frecuencia completa notch para reject_hz
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%se va a intentar hacer lo contrario a un notch (casi un delta de dirac)
%a partir de polos exclusivamente, y después se usará el truco de 
%sacar el 'complemento' del espectro obtenido para hacer el antiantinotch
%es decir el notch

zeros = 1; 

%repite los polos para darle más fuerza a ese pico que se va a generar enm
%'reject_hz', y a su vez aplanar lo que no es esa frecuencia que buscamos rechazar
%este efecto de aplanamiento surge porque la 'H_H' es una normalizada.
poles = [reject_hz reject_hz reject_hz reject_hz reject_hz].*(2*pi*1i)- distance;

if graph_
    plot_poles_and_zeros(poles, zeros);
end

H_H = compute_rect_window(jw, poles, zeros);

%obtiene el angulo H_H, para que después del truco de sacar el
%'complemento' se pueda reconstruir la señal
ang = angle(H_H);               

if graph_
    tit1 = ['Antinotch [ ' num2str(reject_hz)  '  Hz]'];
    plot_all_about_win(freq, time, H_H, tit1 );
end
    
%aplicación del truco
H_H_esp = 1 - abs(compute_rect_window(jw, poles, zeros));

%reconstrucción de H_H con el nuevo espectro
H_H = H_H_esp.*exp(ang.*1i);

if graph_
    tit2 = ['Notch a base de Antinotch [ ' num2str(reject_hz)  '  Hz]'];
    plot_all_about_win(freq, time, H_H, tit2);
end

H_H_C = [ fliplr(H_H(1:end)) conj(H_H(2:end))];

%Generar respuesta en frecuencia completa del filtro
%H_H_C = [fliplr(H_H(1:end-1)) conj( H_H(2:end) ) ]; %flip left to right
%H_H_C = [fliplr(H_H(1:end)) fliplr(conj( fliplr(H_H(2:end))) ) ]; %flip left to right
end

