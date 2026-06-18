//
//  touchidTests.swift
//  touchidTests
//
//  Created by Gareth on 5/23/15.
//  Copyright (c) 2015 GarethPaul. All rights reserved.
//

import UIKit
import XCTest
import LocalAuthentication
@testable import touchid

final class touchidTests: XCTestCase {

    func testAuthenticationResultMessageHandlesSuccessfulResult() {
        let controller = ViewController()
        XCTAssertEqual(controller.authenticationResultMessage(success: true, error: nil), "authentication succeeded")
    }

    func testAuthenticationResultMessageHandlesFailedResult() {
        let controller = ViewController()
        let error = NSError(domain: LAError.errorDomain, code: LAError.Code.authenticationFailed.rawValue)
        XCTAssertEqual(controller.authenticationResultMessage(success: false, error: error), "authentication failed")
    }

    func testAuthenticationResultMessageRejectsContradictorySuccess() {
        let controller = ViewController()
        let error = NSError(domain: LAError.errorDomain, code: LAError.Code.authenticationFailed.rawValue)
        XCTAssertEqual(controller.authenticationResultMessage(success: true, error: error), "authentication failed")
    }

    func testAuthenticationFailureReasonHandlesUnavailableBiometrics() {
        let controller = ViewController()
        let error = NSError(domain: LAError.errorDomain, code: LAError.Code.biometryNotAvailable.rawValue)
        XCTAssertEqual(controller.authenticationFailureReason(error), "biometric authentication unavailable", "Unavailable biometrics should stay local and sensor-neutral")
    }

    func testAuthenticationFailureReasonHandlesUnenrolledBiometrics() {
        let controller = ViewController()
        let error = NSError(domain: LAError.errorDomain, code: LAError.Code.biometryNotEnrolled.rawValue)
        XCTAssertEqual(controller.authenticationFailureReason(error), "biometric authentication not enrolled", "Enrollment guidance should not name an unavailable sensor type")
    }

    func testAuthenticationFailureReasonHandlesMissingError() {
        let controller = ViewController()
        XCTAssertEqual(controller.authenticationFailureReason(nil), "unable to authenticate user", "Missing LocalAuthentication errors should stay generic")
    }

    func testAuthenticationFailureReasonRejectsOtherErrorDomains() {
        let controller = ViewController()
        let error = NSError(domain: "ExampleErrorDomain", code: LAError.Code.biometryNotAvailable.rawValue)
        XCTAssertEqual(controller.authenticationFailureReason(error), "unable to authenticate user", "Non-LocalAuthentication errors should stay generic")
    }

    func testAuthenticationFailureReasonHandlesUserFallback() {
        let controller = ViewController()
        let error = NSError(domain: LAError.errorDomain, code: LAError.Code.userFallback.rawValue)
        XCTAssertEqual(controller.authenticationFailureReason(error), "user chose fallback authentication", "Fallback choices should not imply a password flow exists")
    }

    func testAuthenticationFailureReasonHandlesBiometryLockout() {
        let controller = ViewController()
        let error = NSError(domain: LAError.errorDomain, code: LAError.Code.biometryLockout.rawValue)
        XCTAssertEqual(controller.authenticationFailureReason(error), "biometric authentication locked")
    }

}
