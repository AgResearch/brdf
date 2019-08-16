--
-- Name: biosamplingfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosamplingfact FROM PUBLIC;
REVOKE ALL ON TABLE biosamplingfact FROM agrbrdf;
GRANT ALL ON TABLE biosamplingfact TO agrbrdf;
GRANT SELECT ON TABLE biosamplingfact TO gbs;


