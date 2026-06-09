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

class touchidTests: XCTestCase {

    func testAuthenticationFailureReasonHandlesUnavailableTouchID() {
        let controller = ViewController()
        let error = NSError(domain: LAErrorDomain, code: LAError.TouchIDNotAvailable.rawValue, userInfo: nil)
        XCTAssertEqual(controller.authenticationFailureReason(error), "touch id unavailable", "Unavailable Touch ID should stay local and specific")
    }

    func testAuthenticationFailureReasonHandlesMissingError() {
        let controller = ViewController()
        XCTAssertEqual(controller.authenticationFailureReason(nil), "unable to authenticate user", "Missing LocalAuthentication errors should stay generic")
    }

    func testAuthenticationFailureReasonRejectsOtherErrorDomains() {
        let controller = ViewController()
        let error = NSError(domain: "ExampleErrorDomain", code: LAError.TouchIDNotAvailable.rawValue, userInfo: nil)
        XCTAssertEqual(controller.authenticationFailureReason(error), "unable to authenticate user", "Non-LocalAuthentication errors should stay generic")
    }

    func testAuthenticationFailureReasonHandlesUserFallback() {
        let controller = ViewController()
        let error = NSError(domain: LAErrorDomain, code: LAError.UserFallback.rawValue, userInfo: nil)
        XCTAssertEqual(controller.authenticationFailureReason(error), "user chose fallback authentication", "Fallback choices should not imply a password flow exists")
    }

}
