--
-- Name: sequencealignmentfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE sequencealignmentfact FROM PUBLIC;
REVOKE ALL ON TABLE sequencealignmentfact FROM agrbrdf;
GRANT ALL ON TABLE sequencealignmentfact TO agrbrdf;
GRANT SELECT ON TABLE sequencealignmentfact TO gbs;


