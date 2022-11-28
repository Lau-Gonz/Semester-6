% Filtro pasa banda
clear all
close all
clc

L = 10000; % Longitud de la señal (numero de muestras)
T = 100; % Duración de la señal
Fs = L/T; % Frecuencia de muestreo
f = Fs*(0:L/2)/L; % Vector de Frecuencias

t = linspace(0,T,L);
y = sin(2*pi*t);
w = f*2*pi;

z_0 = 0;
z_1 = -0.5+0.5*2*pi*1i;
z_2 = -0.5+3.5*2*pi*1i;
z_3 = 4*2*pi*1i;
p_1 = -0.5+1i*2*pi;
p_2 = -0.5+2i*2*pi;
p_3 = -0.5+1.5i*2*pi;

num = (1i.*w-z_0).*(1i.*w-z_1).*(1i.*w-conj(z_1)).*(1i.*w-z_2).*(1i.*w-conj(z_2)).*(1i.*w-z_3).*(1i.*w-conj(z_3));
den = (1i.*w-p_1).*(1i.*w-conj(p_1)).*(1i.*w-p_1).*(1i.*w-conj(p_1)).*(1i.*w-p_2).*(1i.*w-conj(p_2)).*(1i.*w-p_2).*(1i.*w-conj(p_2)).*(1i.*w-p_3).*(1i.*w-conj(p_3));;

H_H = num./den;
% H_H = 1./(1i.*w+0.000001);

figure, subplot(2,4,[1 2])
semilogy(f,abs(H_H))
xlim([0 3])
grid
xlabel('Freq[Hz]')
ylabel('Amplitud [u.a.]')

subplot(2,4,[3 4])
plot(f,angle(H_H))
xlim([0 3])
grid
xlabel('Freq[Hz]')
ylabel('Amplitud [u.a.]')

H_H_C = [H_H(1:end-1) conj(fliplr(H_H(2:end)))];
h_h = real(ifft(H_H_C));

subplot(2,4,[6 7])
plot(t,h_h)
grid
xlabel('time [s]')
ylabel('Amplitud [u.a.]')

Y1 = fft(y);
YF1 = H_H_C.*Y1;
y_f = ifft(YF1,'Symmetric');

figure, plot(t,y)
hold on
plot(t,y_f/max(y_f))
xlabel('time [s]')
ylabel('Amplituide')
legend('Original','Filtrada')



