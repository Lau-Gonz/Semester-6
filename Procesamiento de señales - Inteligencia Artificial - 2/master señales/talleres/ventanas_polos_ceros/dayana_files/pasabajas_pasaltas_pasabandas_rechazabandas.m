% Filtro pasa banda
clear all
close all
clc
%%

L = 180000; %Longitud de la señal
T = 30;     %Duración de la señal
Fs = L/T;   %Frecuencia de muestreo

%vector entre 0 y 1/2 multiplicado por Fs
%vector entre 0 y Fs/2
f = Fs*(0:L/2)/L;

%vector de tiempo de 10000 elementos
t = linspace(0, T, L);
y = sin(2*pi*t);        %señal sinusoidal
w = f*2*pi;             %vector omega, de frecuencias angulares
epsilon = 0.00000000001;

realPart1 = [ log(linspace(epsilon, 999, 7) + epsilon )]; 
zeros1 = [ linspace(0, 999, 7)*2*pi ].*1i - realPart1; 


zeros2 = [ linspace(2001, 3000,7)*2*pi ].*1i;

realPart2 = [ log( linspace(2001, 3000,7) ).^-1 ];
zeros2 = [ linspace(2001, 3000,7)*2*pi ].*1i - realPart2;

zeros = [zeros1 zeros2];

Realpart3 = [0.00001  0.05  0.001  0.1  1  1  1  1  1  0.1  0.1  0.001  0.001 0.000001];
poles = [ linspace(1000, 2000, 14)*2*pi ].*1i-Realpart3;



H_H  = compute_rect_window(w,poles,zeros)
%H_H = high_pass_win(w, 1, zeros);


%% 

%plot de la magnitud en frecuencia
%plot de 2 filas 4 columnas donde para este plot
%en particular se toma la primera y la segunda celda
figure, subplot(2,4, [1 2])
semilogy(f, abs(H_H))
grid on
xlabel('Freq [Hz]')
ylabel('Amplitud [u.a.]') %unidades arbitrarias

%plot del angulo de la frecuencia
%para este plot en particular se toma la 3ra y la 4ta celda
subplot(2,4, [3 4])
plot(f, angle(H_H))
grid on
xlabel('Freq [Hz]')
ylabel('Angulo [u.a.]') %unidades arbitrarias

%Generar respuesta en frecuencia completa del filtro
L_H_C = [H_H(1:end-1) conj( fliplr(H_H(2:end)) ) ]; %flip left to right
    
%Obtener la respuesta al impulso 
l_h = real(ifft(L_H_C));    %por errores numéricos la ifft no es puramente real 
                            %por lo tanto se le saca la parte real
                                
%para este plot en particular se toma la 6ta y la 7tima celda
subplot(2, 4, [6 7])
plot(t(1:end/2), l_h(1:end/2))      %por la simetría la señal se puede cortar a la mitad
grid on
xlabel('time [s]')
ylabel('Amplitud [u.a.]') %unidades arbitrarias
