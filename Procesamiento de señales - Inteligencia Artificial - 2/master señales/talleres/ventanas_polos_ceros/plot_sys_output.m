function [y_f] = plot_sys_output(y, time, H_H_C)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   Input: y -> puntos de la señal a filtrar
%          time ->  vector del tiempo   
%          H_H_C ->  respuesta en frecuencia completa del filtro
%
%   Output: y_f -> señal filtrada con H_H_C
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Y3 = fft(y);       %necesito el espectro de fourier para filtrarle las freqs
YF3 = H_H_C .* Y3; %salida del filtro

%obtiene la señal filtrada
y_f = ifft(YF3, 'Symmetric');


figure, plot(time, y)
hold on 
plot(time, y_f/max(y_f))
xlabel('time [s]')
ylabel('Amplitud [u.a.]') %unidades arbitrarias     
legend('Original', 'Filtered')
hold off

end

