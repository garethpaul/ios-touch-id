import LocalAuthentication
import UIKit

class ViewController: UIViewController {
    private let authenticateButton = UIButton(type: .system)
    private var authenticationInProgress = false
    private var authenticationMessage = "authentication not started"
    private var authenticationContext: LAContext?
    private var authenticationAttempt: UUID?

    override func viewDidLoad() {
        super.viewDidLoad()
        configureAuthenticationButton()
    }

    override func viewDidDisappear(_ animated: Bool) {
        super.viewDidDisappear(animated)
        authenticationAttempt = nil
        authenticationContext?.invalidate()
        authenticationContext = nil
        authenticationInProgress = false
        authenticateButton.isEnabled = true
        describeReadyAuthenticationButton()
    }

    private func configureAuthenticationButton() {
        describeReadyAuthenticationButton()
        authenticateButton.addTarget(self, action: #selector(authenticateButtonTapped(_:)), for: .touchUpInside)
        authenticateButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(authenticateButton)

        NSLayoutConstraint.activate([
            authenticateButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            authenticateButton.centerYAnchor.constraint(equalTo: view.centerYAnchor),
        ])
    }

    private func describeReadyAuthenticationButton() {
        authenticateButton.setTitle("Authenticate Locally", for: .normal)
        authenticateButton.accessibilityLabel = "Authenticate Locally"
        authenticateButton.accessibilityHint = "Starts local biometric authentication without sending credentials"
    }

    private func announceAuthenticationStatus(_ message: String) {
        UIAccessibility.post(notification: .announcement, argument: message)
    }

    @IBAction @objc func authenticateButtonTapped(_ sender: Any) {
        authenticateWithBiometrics()
    }

    private func authenticateWithBiometrics() {
        guard !authenticationInProgress else {
            return
        }

        authenticationInProgress = true
        authenticationMessage = "authentication started"
        authenticateButton.setTitle("Authenticating...", for: .disabled)
        authenticateButton.isEnabled = false
        authenticateButton.accessibilityLabel = "Authenticating Locally"
        authenticateButton.accessibilityHint = "Local biometric authentication is in progress"
        announceAuthenticationStatus("Authenticating Locally")

        let context = LAContext()
        let attempt = UUID()
        authenticationContext = context
        authenticationAttempt = attempt
        var error: NSError?

        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            finishAuthentication(attempt: attempt, message: authenticationFailureReason(error))
            return
        }

        context.localizedFallbackTitle = ""
        context.evaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            localizedReason: "Authenticate locally to continue"
        ) { [weak self] success, authenticationError in
            DispatchQueue.main.async {
                let message = self?.authenticationResultMessage(
                    success: success,
                    error: authenticationError
                ) ?? "unable to authenticate user"
                self?.finishAuthentication(attempt: attempt, message: message)
            }
        }
    }

    private func finishAuthentication(attempt: UUID, message: String) {
        guard authenticationAttempt == attempt else {
            return
        }

        authenticationContext?.invalidate()
        authenticationAttempt = nil
        authenticationContext = nil
        authenticationInProgress = false
        authenticateButton.isEnabled = true
        describeReadyAuthenticationButton()
        authenticationMessage = message
        announceAuthenticationStatus(message)
    }

    func authenticationResultMessage(success: Bool, error: Error?) -> String {
        guard success, error == nil else {
            return authenticationFailureReason(error)
        }

        return "authentication succeeded"
    }

    func authenticationFailureReason(_ error: Error?) -> String {
        guard let error = error else {
            return "unable to authenticate user"
        }

        let authenticationError = error as NSError
        guard authenticationError.domain == LAError.errorDomain,
              let code = LAError.Code(rawValue: authenticationError.code) else {
            return "unable to authenticate user"
        }

        switch code {
        case .authenticationFailed:
            return "authentication failed"
        case .userCancel:
            return "user canceled authentication"
        case .systemCancel:
            return "system canceled authentication"
        case .appCancel:
            return "app canceled authentication"
        case .invalidContext:
            return "authentication context invalid"
        case .passcodeNotSet:
            return "passcode not set"
        case .userFallback:
            return "user chose fallback authentication"
        case .biometryNotAvailable:
            return "biometric authentication unavailable"
        case .biometryNotEnrolled:
            return "biometric authentication not enrolled"
        case .biometryLockout:
            return "biometric authentication locked"
        default:
            return "unable to authenticate user"
        }
    }
}
