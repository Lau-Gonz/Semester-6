L = 10000;  %Longitud de la señal
T = 100;    %Duración de la señal
Fs = L/T;   %Frecuencia de muestreo

%vector entre 0 y 1/2 multiplicado por Fs
%vector entre 0 y Fs/2
f = Fs*(0:L/2)/L;

%vector de tiempo de 10000 elementos
t = linspace(0, T, L);
y = sin(2*pi*t);        %señal sinusoidal
w = f*2*pi;             %vector omega, de frecuencias angulares

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Filtro pasa alto más sencillo 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%una función que crece linealmente al estilo de y = x,
%esto es realmente H(s) = s, desarrollando sabemos que 
%H(s) = Y(s)/X(s); y despejando,  Y(s) = s * X(s), vea que esto es 
%la derivada de la señal X

%high pass H
H_H = 1i.*w; %crea jw (j omega) 

%plot de la magnitud en frecuencia
%plot de 2 filas 4 columnas donde para este plot
%en particular se toma la primera y la segunda celda
figure, subplot(2,4, [1 2])
semilogy(f, abs(H_H))
grid on
xlim([0 3])
xlabel('Freq [Hz]')
ylabel('Amplitud [u.a.]') %unidades arbitrarias

%plot del angulo de la frecuencia
%para este plot en particular se toma la 3ra y la 4ta celda
subplot(2,4, [3 4])
plot(f, angle(H_H))
grid on
xlim([0 3])
xlabel('Freq [Hz]')
ylabel('Angulo [u.a.]') %unidades arbitrarias

%Generar respuesta en frecuencia completa del filtro
H_H_C = [H_H(1:end-1) conj( fliplr(H_H(2:end)) ) ]; %flip left to right
    
%Obtener la respuesta al impulso 
h_h = real(ifft(H_H_C));    %por errores numéricos la ifft no es puramente real 
                            %por lo tanto se le saca la parte real
                                
%para este plot en particular se toma la 6ta y la 7tima celda
subplot(2,4, [6 7])
plot(t(1:end/2), h_h(1:end/2))      %por la simetría la señal se puede cortar a la mitad
grid on
xlabel('time [s]')
ylabel('Amplitud [u.a.]') %unidades arbitrarias                                       

%% Obtener salida del sistema

Y3 = fft(y);       %necesito el espectro de fourier para filtrarle las freqs
YF3 = H_H_C .* Y3; %salida del filtro

%obtiene la señal filtrada
y_f = ifft(YF3, 'Symmetric');

figure, plot(t, y)
hold on 
plot(t, y_f/max(y_f))
xlabel('time [s]')
ylabel('Amplitud [u.a.]') %unidades arbitrarias     
legend('Original', 'Filtered')



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Filtro pasa bajo más sencillo 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%un intregrador.
%esto es realmente H(s) = 1/s, desarrollando sabemos que 
%H(s) = Y(s)/X(s); y despejando,  Y(s) = X(s)/s, vea que esto es 
% s * Y(s) = X(s) -> esto es: la derivada de la salida es igual a la
% entrada [entonces estamos integrando]

epsilon = 0.000001;

%low pass H
L_H = 1./(1i.*w + epsilon); %crea jw (j omega) 
                             %dado que se quiere evitar la división por
                             %cero por estabilidad numérica se suma el
                             %epsilon
                             
%plot de la magnitud en frecuencia
%plot de 2 filas 4 columnas donde para este plot
%en particular se toma la primera y la segunda celda
figure, subplot(2,4, [1 2])
semilogy(f, abs(L_H))
grid on
xlim([0 3])
xlabel('Freq [Hz]')
ylabel('Amplitud [u.a.]') %unidades arbitrarias

%plot del angulo de la frecuencia
%para este plot en particular se toma la 3ra y la 4ta celda
subplot(2,4, [3 4])
plot(f, angle(L_H))
grid on
xlim([0 3])
xlabel('Freq [Hz]')
ylabel('Angulo [u.a.]') %unidades arbitrarias

%Generar respuesta en frecuencia completa del filtro
L_H_C = [L_H(1:end-1) conj( fliplr(L_H(2:end)) ) ]; %flip left to right
    
%Obtener la respuesta al impulso 
l_h = real(ifft(L_H_C));    %por errores numéricos la ifft no es puramente real 
                            %por lo tanto se le saca la parte real
                                
%para este plot en particular se toma la 6ta y la 7tima celda
subplot(2,4, [6 7])
plot(t(1:end/2), l_h(1:end/2))      %por la simetría la señal se puede cortar a la mitad
grid on
xlabel('time [s]')
ylabel('Amplitud [u.a.]') %unidades arbitrarias                                       

%% Obtener salida del sistema

Y3 = fft(y);      %necesito el espectro de fourier para filtrarle las freqs
YF3 = pb_H_C .* Y3; %salida del filtro

%obtiene la señal filtrada
y_f = ifft(YF3, 'Symmetric');

figure, plot(t, y)
hold on 
plot(t, y_f/max(y_f))
xlabel('time [s]')
ylabel('Amplitud [u.a.]') %unidades arbitrarias     
legend('Original', 'Filtered')


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Filtro pasa banda 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%ubico ceros
z0 = 0;                   %ubico un cero en el origen  
z1 = -0.5 + 0.5*2*pi* 1i; %ubico un cero en 1/2 + 0.5(jw)
z2 = -0.5 + 3.5*2*pi* 1i; %ubico un cero en 1/2 + 3.5(jw)
z3 = 4*2*pi*1i;           %ubico un cero en 4(jw)

%ubico polos

p1 = -0.5 + 1i*2*pi; 
p2 = -0.5 + 2i*2*pi;
p3 = -0.8 + 1.5i*2*pi;

%Hago el denominador de la función de transferencia H(s) = Y(s)/X(s)

num = (1i.*w - z0).*(1i.*w - z1).*(1i.*w - conj(z1)).*(1i.*w - z2).*(1i.*w - conj(z2)).*(1i.*w - z3).*(1i.*w - conj(z3));
den = (1i.*w - p1).*(1i.*w - conj(p1)).*(1i.*w - p1).*(1i.*w - conj(p1)).*(1i.*w - p2).*(1i.*w - conj(p2)).*(1i.*w - p2).*(1i.*w - conj(p2)).*(1i.*w - p3).*(1i.*w - conj(p3)).*(1i.*w - p3).*(1i.*w - conj(p3));

%pasabanda H
pb_H = num ./ den;



%% plots de frecuencia/angulo del filtro pasa bandas

figure, subplot(2,4, [1 2])
semilogy(f, abs(pb_H))
grid on
xlim([0 3])
xlabel('Freq [Hz]')
ylabel('Amplitud [u.a.]') %unidades arbitrarias

%plot del angulo de la frecuencia
%para este plot en particular se toma la 3ra y la 4ta celda
subplot(2,4, [3 4])
plot(f, angle(pb_H))
grid on
xlim([0 3])
xlabel('Freq [Hz]')
ylabel('Angulo [u.a.]') %unidades arbitrarias

%Generar respuesta en frecuencia completa del filtro
pb_H_C = [pb_H(1:end-1) conj( fliplr(pb_H(2:end)) ) ]; %flip left to right
    
%Obtener la respuesta al impulso 
pb_h = real(ifft(pb_H_C));    %por errores numéricos la ifft no es puramente real 
                            %por lo tanto se le saca la parte real
                                
%para este plot en particular se toma la 6ta y la 7tima celda
subplot(2,4, [6 7])
plot(t(1:end/2), pb_h(1:end/2))      %por la simetría la señal se puede cortar a la mitad
grid on
xlabel('time [s]')
ylabel('Amplitud [u.a.]') %unidades arbitrarias                   

%% Obtener salida del sistema

Y3 = fft(y);      %necesito el espectro de fourier para filtrarle las freqs
YF3 = pb_H_C .* Y3; %salida del filtro

%obtiene la señal filtrada
y_f = ifft(YF3, 'Symmetric');

figure, plot(t, y)
hold on 
plot(t, y_f/max(y_f))
xlabel('time [s]')
ylabel('Amplitud [u.a.]') %unidades arbitrarias     
legend('Original', 'Filtered')






