--
-- Name: geosubmissiondata; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geosubmissiondata FROM PUBLIC;
REVOKE ALL ON TABLE geosubmissiondata FROM agrbrdf;
GRANT ALL ON TABLE geosubmissiondata TO agrbrdf;
GRANT SELECT ON TABLE geosubmissiondata TO gbs;


