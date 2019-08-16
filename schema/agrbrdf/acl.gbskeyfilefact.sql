--
-- Name: gbskeyfilefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE gbskeyfilefact FROM PUBLIC;
REVOKE ALL ON TABLE gbskeyfilefact FROM agrbrdf;
GRANT ALL ON TABLE gbskeyfilefact TO agrbrdf;
GRANT SELECT ON TABLE gbskeyfilefact TO gbs;


